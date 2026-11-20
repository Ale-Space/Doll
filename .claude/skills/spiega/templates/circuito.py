"""TEMPLATE CIRCUITO (Elettrotecnica, reti in continua): legge dei nodi e teorema di Thévenin, VISTI.

Kit: kit/circuiti_kit.py (istruzioni d'uso nel suo docstring). Struttura in atti di guide/manim.md §3.

Rete (griglia 4 x 3): a sinistra V1 = 10 V; in alto R1 = 2 Ω fino al nodo B; dal nodo B scende il ramo
R3 = 2 Ω + V2 = 4 V (il "+" in alto, nodo C fra i due); a destra il carico RL = 6 Ω; sotto la massa 0.
Numeri (analisi nodale esatta con SymPy, verificati qui sotto con assert, Kirchhoff e Tellegen):
  potenziali   V_A = 10 V,  V_B = 6 V,  V_C = 4 V,  V_0 = 0
  correnti     I_1 = (10 - 6)/2 = 2 A   (in R1, verso B)
               I_3 = (6 - 4)/2 = 1 A    (in R3, verso il basso: entra nel "+" di V2, che ASSORBE 4 W)
               I_L = 6/6 = 1 A          (nel carico)            nodo B: 2 = 1 + 1
  potenze      V1 eroga 20 W; R1 8 W, R3 2 W, RL 6 W, V2 assorbe 4 W: 20 = 8 + 2 + 6 + 4 (Tellegen)
  Thévenin ai morsetti B-0 (tolto RL):  V_th = (10/2 + 4/2)/(1/2 + 1/2) = 7 V,  R_th = 2 ∥ 2 = 1 Ω
               I_L = V_th/(R_th + R_L) = 7/7 = 1 A,  V_B = 7 R_L/(1 + R_L) = 6 V
  carico che varia (atto 3):  R_L = 2 Ω -> I_L = 7/3 = 2,33 A;  R_L = 12 Ω -> I_L = 7/13 = 0,54 A
               (in tutta la corsa 2-12 Ω V_B resta sopra 4 V: I_3 non cambia verso)

Copione (≈ 37 s; timestamp misurati sul render):
| t (s)     | Cosa si vede                          | Cosa si muove                              | Didascalia |
|-----------|---------------------------------------|--------------------------------------------|------------|
| 0-2,5     | titolo, enunciato                     | -                                          | - |
| 2,5-5,3   | lo schema IEC                         | i fili si tracciano, compaiono i componenti | Due generatori, tre resistori: chi spinge dove? |
| 5,3-8,3   | puntini su tutti i fili               | le correnti scorrono (V2 è attraversato dal + al -: assorbe) | I puntini scorrono: più veloci, più corrente |
| 8,3-11,6  | frecce in B: 2,00 A, 1,00 A, 1,00 A   | il nodo B lampeggia                        | Nel nodo B: entrano 2 A, escono 1 + 1 |
| 11,6-15   | fili colorati, scala dei potenziali   | il colore si accende (A 10, B 6, C 4, 0 V)  | Il colore è il potenziale: cala nei resistori |
| 15-18,6   | rete a sinistra, riquadro tratteggiato| la rete si rimpicciolisce, R_L lampeggia    | Per il carico, il resto è un bipolo |
| 18,6-23,3 | a destra l'equivalente                | una copia scivola a destra (19-20); V1 -> V_th, R1 -> R_th, il ramo R3-V2 scivola dentro e sparisce (20-21,7) | Il resto si richiude: un generatore, una resistenza |
| 23,3-31,3 | due circuiti, stesse frecce su R_L    | R_L: 6 -> 2 Ω (24-26), -> 12 Ω (26-29), -> 6 Ω (29-31): 2,33 A e 0,54 A in tutti e due | Cambio il carico: stessa corrente nei due |
| 31,3-33,5 | slogan                                | i puntini continuano, i riquadri spariscono | Per il carico basta un generatore reale |
| 33,5-36,8 | riquadro del risultato                | -                                          | - |
Gesto visivo: il riquadro "resto della rete" si richiude in V_th + R_th e, mentre il carico cambia, i puntini e
i numeri sul carico restano uguali nei due circuiti.

Per un'altra rete: cambia la descrizione (nodi e rami sulla griglia), ricalcola con risolvi_esatto/thevenin e
aggiorna docstring e didascalie; tieni la struttura. Altre idee con lo stesso kit: sovrapposizione (spegni un
generatore alla volta: i puntini dei due casi si sommano), Norton (generatore_corrente), massimo trasferimento
di potenza (R_L che varia e una barra della potenza), transitorio RC (interruttore_anima + c.transitorio: i
puntini rallentano e si fermano mentre il condensatore si carica).
"""
from doll_kit import *  # noqa: F401,F403  (render.sh mette kit/ nel PYTHONPATH)
from circuiti_kit import *  # noqa: F401,F403
import numpy as np
import sympy as sp

# ---------------------------------------------------------------- la rete (griglia: x 0..4, y 0..3)
RL = ValueTracker(6.0)                      # il carico: un ValueTracker, perché nell'atto 3 varia

rete = Circuito()
rete.nodo("0", (2, 0), massa=True)
rete.nodo("A", (0, 3), etichetta="A", lato_etichetta=UL)
rete.nodo("B", (2, 3), etichetta="B", lato_etichetta=UP)
rete.nodo("C", (2, 1.5), etichetta="C", lato_etichetta=LEFT)
rete.generatore("V1", "0", "A", 10, via=[(0, 0)], su=1, lato=RIGHT)   # su=1: sul tratto x = 0; etichetta dentro
rete.resistore("R1", "A", "B", 2)
rete.resistore("R3", "B", "C", 2, lato=LEFT)
rete.generatore("V2", "0", "C", 4, lato=LEFT)
rete.resistore("RL", "B", "0", RL, via=[(4, 3), (4, 0)], etichetta="R_L")

# ---------------------------------------------------------------- verifica dei numeri (SymPy, esatti)
SOL = rete.risolvi_esatto()
SOL.verifica()                                                   # Kirchhoff ai nodi e Tellegen
assert (SOL.V["A"], SOL.V["B"], SOL.V["C"]) == (10, 6, 4)
assert (SOL.I["R1"], SOL.I["R3"], SOL.I["RL"], SOL.I["V2"]) == (2, 1, 1, -1)
VTH, RTH = rete.thevenin("B", "0", togli=["RL"])
assert (VTH, RTH) == (7, 1)
_r = sp.Symbol("R_L", positive=True)
assert sp.simplify(rete.risolvi_esatto(valori={"RL": _r}).I["RL"] - VTH / (RTH + _r)) == 0   # Thévenin per ogni R_L
for _rl, _il in ((2, sp.Rational(7, 3)), (12, sp.Rational(7, 13))):              # i due carichi dell'atto 3
    _s = rete.risolvi_esatto(valori={"RL": _rl})
    assert _s.I["RL"] == _il and _s.V["B"] > 4                                       # I_3 non cambia verso
assert [SOL.potenza_assorbita(n) for n in ("V1", "R1", "R3", "V2", "RL")] == [-20, 8, 2, 4, 6]

# ---------------------------------------------------------------- l'equivalente di Thévenin (stessa griglia)
equiv = Circuito()
equiv.nodo("0", (2, 0), massa=True)
equiv.nodo("N", (0, 3))
equiv.nodo("B", (2, 3), etichetta="B", lato_etichetta=UP)
equiv.generatore("Vth", "0", "N", float(VTH), via=[(0, 0)], su=1, lato=RIGHT, etichetta=r"V_{th} = 7\,\mathrm{V}")
equiv.resistore("Rth", "N", "B", float(RTH), etichetta=r"R_{th} = 1\,\Omega")
equiv.resistore("RL", "B", "0", RL, via=[(4, 3), (4, 0)], etichetta="R_L")

# ---------------------------------------------------------------- schermo
PASSO = 1.45
O1 = np.array([-4.3, -2.05, 0.0])          # punto (0, 0) della griglia, atti 1-2
SC = 0.72                                   # atto 3: la rete si rimpicciolisce a sinistra...
O1B = np.array([-5.0, -1.7, 0.0])
O2 = O1B + RIGHT * 5.7 * PASSO * SC         # ...e l'equivalente nasce a destra (5,7 celle dopo), alla stessa scala
RESTO = ((-0.55, -0.7), (2.6, 3.55))         # "il resto della rete" in celle: i fili del carico escono in B e in 0
V_SCALA = (0.0, 10.0)                       # scala dei potenziali FISSA per tutto il video


class Esercizio(Scene):
    def construct(self):
        # ---------------- ATTO 0: apertura ----------------
        titolo(self, "Thévenin: la rete si richiude")
        dati(self, r"\text{bipolo lineare}\ \equiv\ V_{th}\ \text{in serie a}\ R_{th}", max_w=5.6)

        # ---------------- ATTO 1: il circuito ----------------
        d = DisegnoCircuito(rete, passo=PASSO, origine=O1, vmin=V_SCALA[0], vmax=V_SCALA[1], size_etichette=34)
        did = cambia_didascalia(self, None, "Due generatori, tre resistori: chi spinge dove?")
        d.mostra(self, run_time=1.8)
        self.wait(0.5)

        # ---------------- ATTO 2: correnti e potenziali ----------------
        did = cambia_didascalia(self, did, "I puntini scorrono: più veloci, più corrente")
        d.avvia_correnti(self, run_time=0.8)
        self.wait(1.8)

        f1 = d.freccia_corrente("R1", dove=0.72, lato=DOWN, tex="")
        f3 = d.freccia_corrente("R3", dove=0.78, lato=RIGHT, tex="")
        fl = d.freccia_corrente("RL", dove=1.3 / 7, lato=UP, tex="")
        did = cambia_didascalia(self, did, "Nel nodo B: entrano 2 A, escono 1 + 1")
        self.play(FadeIn(f1), FadeIn(f3), FadeIn(fl),
                  Flash(d.p((2, 3)), color=C_RIF, line_length=0.25, flash_radius=0.3), run_time=0.9)
        self.wait(2.0)

        scala = d.scala_potenziali(["A", "B", "C", "0"], centro=[4.6, -0.1, 0], altezza=4.2)
        did = cambia_didascalia(self, did, "Il colore è il potenziale: cala nei resistori")
        d.accendi_potenziali(self, FadeIn(scala), run_time=1.4)
        self.wait(1.6)

        # ---------------- ATTO 3: Thévenin visto ----------------
        self.play(FadeOut(scala), FadeOut(f1), FadeOut(f3), FadeOut(did),
                  d.animate.scale(SC, about_point=O1).shift(O1B - O1), run_time=1.2)
        box = d.riquadro(griglia=RESTO)
        did = cambia_didascalia(self, None, "Per il carico, il resto è un bipolo")
        self.play(Create(box), Indicate(d.pezzi("RL"), color=C_RIF, scale_factor=1.04), run_time=1.0)
        self.wait(1.0)

        e = DisegnoCircuito(equiv, passo=PASSO * SC, origine=O2, vmin=V_SCALA[0], vmax=V_SCALA[1],
                            size_etichette=34 * SC)
        e.mix.set_value(1.0)
        e.update(0)                                              # colori del potenziale già accesi
        box_e = e.riquadro(griglia=RESTO)
        # 1) una copia di tutta la rete scivola a destra; 2) lì, dentro lo stesso riquadro, il resto si richiude
        nomi = ("V1", "R1", "R3", "V2", "RL")
        copia = {n: d.pezzi(n).copy() for n in nomi}
        nodi_c = {n: d.pezzi(nodi=(n,)).copy() for n in ("A", "B", "C", "0")}
        box_c = box.copy()
        did = cambia_didascalia(self, did, "Il resto si richiude: un generatore, una resistenza")
        scivola = VGroup(*copia.values(), *nodi_c.values(), box_c)
        self.play(scivola.animate.shift(O2 - O1B), run_time=1.1)
        self.remove(scivola)
        self.add(*scivola)              # i pezzi, uno per uno: così ognuno può sparire o trasformarsi da solo
        # V1 -> V_th e R1 -> R_th sul posto; il ramo centrale (R3, V2) scivola dentro di loro e sparisce
        self.play(ReplacementTransform(copia["V1"], e.pezzi("Vth")), ReplacementTransform(copia["R1"], e.pezzi("Rth")),
                  *[FadeOut(m, shift=LEFT * 2 * PASSO * SC, scale=0.6) for m in (copia["R3"], copia["V2"], nodi_c["C"])],
                  FadeOut(nodi_c["A"]),           # N non ha etichetta: un Transform verso un gruppo vuoto vola in (0, 0)
                  ReplacementTransform(nodi_c["B"], e.pezzi(nodi=("B",))),
                  ReplacementTransform(nodi_c["0"], e.pezzi(nodi=("0",))),
                  ReplacementTransform(copia["RL"], e.pezzi("RL")), ReplacementTransform(box_c, box_e),
                  run_time=1.6)
        e.consolida(self)
        self.bring_to_front(box_e)
        fl_e = e.freccia_corrente("RL", dove=1.3 / 7, lato=UP, tex="")
        tl = d.tensione("RL", lato=LEFT)
        tl_e = e.tensione("RL", lato=LEFT)
        e.avvia_correnti(self, FadeIn(fl_e), FadeIn(tl), FadeIn(tl_e), run_time=0.8)
        self.wait(0.8)

        carico = numero_vivo(self, lambda: "carico  " + virgola(RL.get_value(), 1) + " Ω", [0.75, 2.55, 0],
                             colore=C_TESTO, size=28, allinea=ORIGIN)
        did = cambia_didascalia(self, did, "Cambio il carico: stessa corrente nei due", )
        self.play(FadeIn(carico), run_time=0.4)
        self.play(RL.animate.set_value(2.0), run_time=2.2, rate_func=smooth)
        self.play(RL.animate.set_value(12.0), run_time=3.0, rate_func=smooth)
        self.play(RL.animate.set_value(6.0), run_time=2.0, rate_func=smooth)
        did = cambia_didascalia(self, did, "Per il carico basta un generatore reale", colore=C_ACCENTO)
        self.wait(1.4)
        self.play(FadeOut(box), FadeOut(box_e), run_time=0.4)

        # ---------------- ATTO 5: risultato ----------------
        carico.clear_updaters()
        risultato_angolo(self, r"V_{th} = 7\,\mathrm{V},\quad R_{th} = 1\,\Omega,\quad "
                               r"I_L = \frac{V_{th}}{R_{th} + R_L} = 1\,\mathrm{A}",
                         vecchia_didascalia=did, attesa=2.2)
