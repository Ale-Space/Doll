"""Helper condivisi per le scene della skill spiega.

IL VIDEO È SOLO VISUALIZZAZIONE. Le derivazioni complete le scrive Claude in chat e nella dispensa.
Niente paragrafi, niente elenchi di passaggi algebrici. Durata secondo l'impegno (guide/manim.md §2.8):
veloce 20-45 s, normale 45-90 s, approfondito 90-180 s.

Struttura tipica:
  titolo(...)            -> 2 s: titolo breve, poi va nell'angolo in alto a sinistra
  dati(...)              -> la matrice / la funzione / i dati restano in alto a destra
  capitolo(...)          -> (approfondito) nome del capitolo, piccolo, sotto il titolo
  ... visualizzazione ... -> ValueTracker, trasformazioni, cose che si muovono
  didascalia(...)        -> 8 / 10 / 12 parole al massimo (veloce / normale / approfondito): DOVE guardare
  formula_chiave(...)    -> (normale, approfondito) la formula del passaggio ACCANTO all'oggetto, una per volta
  risultato_angolo(...)  -> alla fine il risultato in un riquadro, SOPRA la scena

Funzionano anche in ThreeDScene: il testo resta fisso rispetto alla camera.

Layout: zona sicura |x| <= 6.6, |y| <= 3.6.
  alto-sx: titolo | alto-dx: dati | basso: didascalia | centro: la visualizzazione.
"""
from __future__ import annotations

from manim import *

C_TESTO = WHITE
C_ACCENTO = YELLOW
C_A = BLUE_C
C_B = GREEN_C
C_C = RED_C
C_D = PURPLE_B
C_TENUE = GREY_B


def _fissa(scene: Scene, *ms: Mobject) -> None:
    """In una ThreeDScene il testo deve restare fermo rispetto alla camera."""
    if isinstance(scene, ThreeDScene):
        scene.add_fixed_in_frame_mobjects(*ms)


def fit(m: Mobject, max_w: float = 12.6, max_h: float = 6.6) -> Mobject:
    """Rimpicciolisce m finché sta in max_w x max_h (non ingrandisce mai)."""
    if m.width > max_w:
        m.scale_to_fit_width(max_w)
    if m.height > max_h:
        m.scale_to_fit_height(max_h)
    return m


def titolo(scene: Scene, testo: str) -> Text:
    """Titolo breve (3-5 parole) al centro per un attimo, poi si sposta in alto a sinistra."""
    t = Text(testo, font_size=44, color=C_ACCENTO, weight=BOLD)
    fit(t, max_w=11)
    _fissa(scene, t)
    scene.play(Write(t), run_time=0.8)
    scene.wait(0.6)
    piccolo = Text(testo, font_size=24, color=C_TENUE)
    fit(piccolo, max_w=6).to_corner(UL, buff=0.3)
    scene.play(Transform(t, piccolo), run_time=0.6)
    return t


def dati(scene: Scene, latex: str, font_size: int = 36, max_w: float = 5.5) -> MathTex:
    """I dati dell'esercizio (matrice, funzione, valori) fissi in alto a destra, con sfondo.

    max_w limita la larghezza: alzalo (fino a ~7) solo se i dati sono larghi e non coprono nulla.
    """
    m = MathTex(latex, font_size=font_size)
    fit(m, max_w=max_w, max_h=2.4)
    m.to_corner(UR, buff=0.3)
    m.add_background_rectangle(opacity=0.85, buff=0.15)
    _fissa(scene, m)
    scene.play(FadeIn(m), run_time=0.5)
    return m


def didascalia(testo: str, colore=C_TESTO, size: int = 28) -> Text:
    """Frase brevissima in basso: dice DOVE guardare, non spiega."""
    t = Text(testo, font_size=size, color=colore)
    fit(t, max_w=12)
    t.to_edge(DOWN, buff=0.35)
    t.add_background_rectangle(opacity=0.8, buff=0.12)
    return t


def cambia_didascalia(scene: Scene, vecchia: Mobject | None, testo: str, **kw) -> Text:
    nuova = didascalia(testo, **kw)
    _fissa(scene, nuova)
    if vecchia is None:
        scene.play(FadeIn(nuova), run_time=0.4)
    else:
        scene.play(FadeOut(vecchia), FadeIn(nuova), run_time=0.4)
    return nuova


def capitolo(scene: Scene, testo: str, vecchio: Mobject | None = None, numero: int | None = None) -> Text:
    """Impegno approfondito: nome del capitolo (2-4 parole), piccolo e tenue, sotto il titolo in alto a sinistra.

    Non è una schermata: compare mentre la scena continua. Esempio:
        cap = capitolo(self, "Primo Lagrange", numero=2)
        ...
        cap = capitolo(self, "Secondo Lagrange", vecchio=cap, numero=3)
    """
    scritta = f"{numero}. {testo}" if numero is not None else testo
    t = Text(scritta, font_size=22, color=C_ACCENTO)
    fit(t, max_w=5.5)
    t.to_corner(UL, buff=0.3).shift(DOWN * 0.45)
    _fissa(scene, t)
    if vecchio is None:
        scene.play(FadeIn(t, shift=RIGHT * 0.2), run_time=0.4)
    else:
        scene.play(FadeOut(vecchio), FadeIn(t, shift=RIGHT * 0.2), run_time=0.4)
    return t


def formula_chiave(scene: Scene, latex: str, vicino_a: Mobject, direzione=RIGHT, vecchia: Mobject | None = None,
                   colore=C_TESTO, font_size: int = 34, buff: float = 0.3) -> MathTex:
    """Impegno normale/approfondito: la formula del passaggio ACCANTO all'oggetto che la fa vedere.

    Una sola formula a schermo alla volta (passa la precedente in vecchia), corta (una riga), nel colore
    del ruolo che descrive. Non è un elenco di passaggi: è l'etichetta matematica di ciò che si muove.
    In ThreeDScene resta fissa sullo schermo: posizionala con vicino_a = un oggetto già fisso o un Dot 2D.
    """
    f = MathTex(latex, font_size=font_size, color=colore)
    fit(f, max_w=5.5, max_h=1.2)
    f.next_to(vicino_a, direzione, buff=buff)
    f.add_background_rectangle(opacity=0.8, buff=0.1)
    _fissa(scene, f)
    if vecchia is None:
        scene.play(Write(f), run_time=0.8)
    else:
        scene.play(FadeOut(vecchia), Write(f), run_time=0.8)
    return f


def risultato_angolo(scene: Scene, latex: str, vecchia_didascalia: Mobject | None = None,
                     attesa: float = 2.5, posizione=None) -> MathTex:
    """Il risultato in un riquadro, sopra la scena (che resta visibile).

    Di default va in basso; se copre assi o etichette passa posizione (es. RIGHT*4.4 + DOWN*1.5).
    """
    if vecchia_didascalia is not None:
        scene.play(FadeOut(vecchia_didascalia), run_time=0.3)
    r = MathTex(latex, font_size=40)
    fit(r, max_w=11)
    if posizione is None:
        r.to_edge(DOWN, buff=0.45)
    else:
        fit(r, max_w=4.5)
        r.move_to(posizione)
    sfondo = BackgroundRectangle(r, fill_opacity=0.9, buff=0.2)
    box = SurroundingRectangle(r, color=C_ACCENTO, buff=0.2)
    _fissa(scene, sfondo, r, box)
    scene.play(FadeIn(sfondo), Write(r), Create(box), run_time=0.9)
    scene.wait(attesa)
    return r


def pulisci(scene: Scene, *tieni: Mobject, run_time: float = 0.5) -> None:
    """FadeOut di tutto tranne gli oggetti passati in tieni."""
    via = [m for m in scene.mobjects if m not in tieni]
    if via:
        scene.play(*[FadeOut(m) for m in via], run_time=run_time)


# =====================================================================================================
#  STILE DOLL: palette semantica e pezzi pronti. Le scene NON definiscono colori propri (niente "#xxxxxx"):
#  usano queste costanti, cosi' ogni video ha lo stesso aspetto chiunque lo scriva.
#  Sfondo: quello di Manim (nero). Vedi guide/manim.md, "Palette".
# =====================================================================================================
import numpy as _np

# --- ruoli (analisi, geometria) ---
C_OGGETTO = BLUE_C          # l'oggetto principale: grafico, curva, superficie (superfici: BLUE_D/BLUE_E a scacchi)
C_X = BLUE_B                # variabile/direzione 1 (asse x, tratto "cambia solo x", lettura per righe)
C_Y = GREEN_C               # variabile/direzione 2
C_ERRORE = RED_C            # cio' che deve sparire o la differenza: errore, resto, stacco, scarto
C_RIF = YELLOW              # riferimento e accento: piano/retta tangente, valore limite, punto chiave
C_PUNTO = WHITE             # punti generici e loro etichette
C_PIU, C_MENO = YELLOW, PINK  # segni + e - (vertici, contributi)
C_CONTRO = ORANGE           # controesempio / caso patologico
C_MAPPA_PIU, C_MAPPA_MENO = "#FFB050", "#6CBCFF"   # +1 e -1 della mappa di colore (assi, etichette sulla mappa)
# --- ruoli (fisica) ---
C_FORZA = ORANGE            # forze (freccia piena), con scala fissa N -> unita'
C_PESO = RED_C              # peso / forza di gravita'
C_VELOCITA = GREEN_C
C_ACCELERAZIONE = PURPLE_B
C_CAMPO = TEAL_C            # linee di campo, flusso
C_ENERGIA_K, C_ENERGIA_U = BLUE_C, GOLD_C   # cinetica / potenziale (barre)
C_CORPO = GREY_B            # corpi rigidi, aste, superfici di appoggio
SUPERFICIE = dict(checkerboard_colors=[BLUE_D, BLUE_E], stroke_color=BLUE_A)  # Surface(..., **SUPERFICIE)


def fisso(scene: Scene, *ms: Mobject) -> None:
    """ThreeDScene: registra ms come fissi sullo schermo SENZA mostrarli (poi FadeIn/Create)."""
    scene.add_fixed_in_frame_mobjects(*ms)
    scene.remove(*ms)


def orientato(scene: Scene, m: Mobject) -> Mobject:
    """ThreeDScene: etichetta che segue un punto 3D ma resta rivolta alla camera (poi FadeIn)."""
    scene.renderer.camera.add_fixed_orientation_mobjects(m)
    return m


def curva(punti, colore=C_OGGETTO, spessore: float = 4.0) -> VMobject:
    """Spezzata fitta da un array di punti (n, 3): per curve campionate a mano (veloce, anche in 3D)."""
    m = VMobject(stroke_color=colore, stroke_width=spessore)
    m.set_points_as_corners(_np.asarray(punti, dtype=float))
    return m


def virgola(x: float, cifre: int = 2) -> str:
    """Numero all'italiana per i Text: 0,70 e il segno meno tipografico."""
    return f"{x:.{cifre}f}".replace(".", ",").replace("-", "−")


def numero_vivo(scene: Scene, testo_fn, posizione, colore=WHITE, size: int = 25, allinea=LEFT) -> VGroup:
    """Testo che si aggiorna a ogni fotogramma (es. lambda: "R = " + virgola(R())).

    Sicuro anche in ThreeDScene (resta fisso sullo schermo) e senza "immagini fantasma". Va aggiunto con
    scene.add(...) (o FadeIn); a fine uso: m.clear_updaters().
    """
    # Un solo figlio, sempre lo stesso oggetto: lo si aggiorna con become(). Sostituirlo con un Text nuovo
    # lascerebbe disegnato quello vecchio (Manim congela la lista degli oggetti all'inizio di ogni play).
    t = Text(testo_fn(), font_size=size, color=colore).move_to(posizione, aligned_edge=allinea)
    g = VGroup(t)
    if isinstance(scene, ThreeDScene):
        scene.renderer.camera.add_fixed_in_frame_mobjects(t)

    def agg(m, dt):
        nuovo = Text(testo_fn(), font_size=size, color=colore).move_to(posizione, aligned_edge=allinea)
        m.submobjects[0].become(nuovo)

    g.add_updater(agg)
    return g


# --- mappe di colore (una funzione di due variabili come colore: ottima per derivate, densita', campi) ---
_V_STOP = _np.array([-1.6, -1.0, 0.0, 1.0, 1.6])
_C_STOP = _np.array([[191, 239, 255], [46, 134, 222], [28, 28, 42], [240, 127, 19], [255, 242, 168]], float)


def colori_mappa(v):
    """Valori -> RGBA (uint8). Scala fissa per tutti i video: -1 blu, 0 scuro, +1 arancio, +-1,6 chiari."""
    v = _np.asarray(v, dtype=float)
    can = [_np.interp(v, _V_STOP, _C_STOP[:, k]) for k in range(3)]
    return _np.dstack(can + [_np.full_like(can[0], 255.0)]).astype(_np.uint8)


def mappa(fun, x0, x1, y0, y1, n: int = 240, scala: float = 1.0):
    """Array RGBA di fun(x, y)/scala su [x0, x1] x [y0, y1] (prima riga = y1). fun vettorializzata."""
    xs = x0 + (_np.arange(n) + 0.5) / n * (x1 - x0)
    ys = y1 - (_np.arange(n) + 0.5) / n * (y1 - y0)
    return colori_mappa(fun(*_np.meshgrid(xs, ys)) / scala)


def immagine_mappa(arr, lato: float, centro) -> ImageMobject:
    """ImageMobject quadrato da un array di mappa(). Per animarla: m.pixel_array = mappa(...) in un updater."""
    m = ImageMobject(arr)
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    m.scale_to_fit_height(lato)
    m.move_to(centro)
    return m


def barra_colori(v0: float, v1: float, altezza: float, centro, scala: float = 1.0) -> ImageMobject:
    """Legenda verticale della mappa di colore, da v0 (in basso) a v1 (in alto)."""
    vs = _np.linspace(v1, v0, 200)[:, None] / scala
    arr = _np.repeat(colori_mappa(vs), 24, axis=1)
    m = ImageMobject(arr)
    m.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
    m.stretch_to_fit_height(altezza).stretch_to_fit_width(0.3).move_to(centro)
    return m


def freccia_fisica(P, vettore, colore=C_FORZA, scala: float = 0.1, etichetta: str | None = None,
                   size: int = 30) -> VGroup:
    """Vettore fisico con SCALA FISSA (es. 1 N -> 0,1 unita'), dalla punta di applicazione P."""
    P = _np.array([*P[:2], 0.0]) if len(P) == 2 else _np.asarray(P, dtype=float)
    v = _np.array([*vettore[:2], 0.0]) * scala
    g = VGroup(Arrow(P, P + v, buff=0, color=colore, stroke_width=5, max_tip_length_to_length_ratio=0.25))
    if etichetta:
        n = _np.linalg.norm(v) or 1.0
        g.add(MathTex(etichetta, font_size=size, color=colore).move_to(P + v + v / n * 0.3))
    return g
