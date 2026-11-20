/* Doll: helper comuni delle pagine interattive. Inserito da web_build.py.
 *
 * Struttura HTML attesa (vedi templates/web/*.html):
 *   header.doll-top > h1 + div.doll-dati
 *   main.doll-main  > section.doll-vista#vista + aside.doll-pannello#pannello
 *   footer.doll-didascalia#didascalia
 *
 * API principali (oggetto globale Doll):
 *   Doll.slider(parent, {label, min, max, step, value, fmt, onInput})  -> {value(), set(v)}
 *   Doll.scelta(parent, {label, opzioni:[[valore, testo],...], value, onChange}) -> {value(), set(v)}
 *   Doll.bottone(parent, testo, onClick, primario)
 *   Doll.interruttore(parent, {label, value, onChange}) -> {value(), set(v)}   (casella di spunta)
 *   Doll.dati(tex)                    cambia la formula in alto a destra
 *   Doll.lettura(parent, etichetta) -> funzione set(testoOppureTeX)
 *   Doll.bersaglio(parent, {testo, verifica: () => bool, ok}) -> {mostra(v), raggiunto}   "Prova tu" con ✓
 *   Doll.titoletto(parent, testo)
 *   Doll.didascalia(testo)            testo breve in basso (accetta $...$)
 *   Doll.animazione(fn(dt, t))        loop con Play/Pausa -> {play(), pausa(), reset(), attiva}
 *   Doll.guida(passi)                 percorso guidato: [{testo, applica()}], bottoni Indietro/Avanti
 *   Doll.stati(lista)                 stati per il controllo automatico: [{nome, applica()}]
 *   Doll.pronto()                     da chiamare quando la pagina e' disegnata
 *   Doll.tex(el)                      rende le formule $...$ dentro el (KaTeX)
 *   Doll.col                          palette (stessi colori del CSS)
 *   Doll.ruolo                        colori per RUOLO (oggetto, x, y, errore, rif, contro, forza, velocita, campo, ...)
 */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const col = { blu: "#2b6cb0", arancio: "#dd6b20", verde: "#2f855a", rosso: "#c53030", viola: "#6b46c1",
                giallo: "#b7791f", grigio: "#6b6b70", testo: "#1d1d1f", bordo: "#e2e0d8", sfondo: "#ffffff" };
  // RUOLI: lo stesso significato dei colori dei video (guide/manim.md §6). Usa questi, non colori propri.
  const ruolo = { oggetto: col.blu, x: col.blu, y: col.verde, errore: col.rosso, rif: col.giallo, punto: col.testo,
                  piu: col.giallo, meno: "#b83280", contro: col.arancio, forza: col.arancio, peso: col.rosso,
                  velocita: col.verde, accelerazione: col.viola, campo: "#2c7a7b", energiaK: col.blu,
                  energiaU: col.giallo, corpo: col.grigio, tenue: col.grigio };

  function tex(el) {
    if (!el || typeof renderMathInElement !== "function") return;
    renderMathInElement(el, { delimiters: [
      { left: "$$", right: "$$", display: true }, { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false }, { left: "\\[", right: "\\]", display: true }],
      throwOnError: false });
  }
  function box(parent) {
    const d = document.createElement("div"); d.className = "doll-ctrl";
    (typeof parent === "string" ? $(parent) : parent || $("#pannello")).appendChild(d); return d;
  }
  function slider(parent, o) {
    const d = box(parent), fmt = o.fmt || (v => (+v).toFixed(String(o.step ?? 0.01).split(".")[1]?.length || 0));
    d.innerHTML = `<label><span></span><b></b></label><input type="range">`;
    const sp = d.querySelector("span"), b = d.querySelector("b"), inp = d.querySelector("input");
    sp.innerHTML = o.label; tex(sp);
    Object.assign(inp, { min: o.min, max: o.max, step: o.step ?? 0.01, value: o.value ?? o.min });
    const upd = () => { b.textContent = fmt(+inp.value); o.onInput && o.onInput(+inp.value); };
    inp.addEventListener("input", upd); b.textContent = fmt(+inp.value);
    // set(v, true) sposta solo lo slider, senza chiamare onInput
    return { value: () => +inp.value, set: (v, muto) => { inp.value = v; if (muto) b.textContent = fmt(+inp.value); else upd(); }, el: inp };
  }
  function scelta(parent, o) {
    const d = box(parent);
    d.innerHTML = `<label><span></span></label><select></select>`;
    d.querySelector("span").innerHTML = o.label || ""; tex(d.querySelector("span"));
    const s = d.querySelector("select");
    for (const [v, t] of o.opzioni) { const op = document.createElement("option"); op.value = v; op.textContent = t; s.appendChild(op); }
    if (o.value !== undefined) s.value = o.value;
    s.addEventListener("change", () => o.onChange && o.onChange(s.value));
    return { value: () => s.value, set: v => { s.value = v; o.onChange && o.onChange(v); }, el: s };
  }
  function bottone(parent, testo, onClick, primario) {
    const p = typeof parent === "string" ? $(parent) : parent || $("#pannello");
    let riga = p.lastElementChild;
    if (!riga || !riga.classList.contains("doll-riga")) { riga = document.createElement("div"); riga.className = "doll-riga"; p.appendChild(riga); }
    const b = document.createElement("button"); b.className = "doll-btn" + (primario ? " primario" : "");
    b.innerHTML = testo; b.onclick = onClick; riga.appendChild(b); return b;
  }
  function interruttore(parent, o) {
    const d = box(parent); d.classList.add("interruttore");
    d.innerHTML = `<label><input type="checkbox"><span></span></label>`;
    const c = d.querySelector("input"), sp = d.querySelector("span");
    sp.innerHTML = o.label; tex(sp); c.checked = !!o.value;
    c.addEventListener("change", () => o.onChange && o.onChange(c.checked));
    return { value: () => c.checked, set: (v, muto) => { c.checked = !!v; if (!muto && o.onChange) o.onChange(c.checked); }, el: c };
  }
  function dati(t) { const d = $(".doll-dati"); if (d) { d.innerHTML = t; tex(d); } }
  function lettura(parent, etichetta) {
    const p = typeof parent === "string" ? $(parent) : parent || $("#pannello");
    const d = document.createElement("div"); d.className = "doll-lettura";
    d.innerHTML = `<span></span><span></span>`; p.appendChild(d);
    d.firstChild.innerHTML = etichetta; tex(d.firstChild);
    return t => { d.lastChild.innerHTML = t; tex(d.lastChild); };
  }
  // "Prova tu" (guide/didattica.md): un compito con riscontro immediato. verifica() restituisce true quando
  // il bersaglio e' raggiunto; si ricontrolla da solo 4 volte al secondo. Nascosto finche' non lo mostri.
  function bersaglio(parent, o) {
    const p = typeof parent === "string" ? $(parent) : parent || $("#pannello");
    const d = document.createElement("div"); d.className = "doll-bersaglio"; d.style.display = "none"; p.appendChild(d);
    let fatto = null;
    const agg = () => {
      let r = false; try { r = !!o.verifica(); } catch (e) { r = false; }
      if (r === fatto) return; fatto = r;
      d.classList.toggle("ok", r);
      d.innerHTML = r ? `✓ ${o.ok || "Giusto!"}` : `◎ ${o.testo}`; tex(d);
    };
    agg(); setInterval(agg, 250);
    return { mostra: (v = true) => { d.style.display = v ? "" : "none"; agg(); }, get raggiunto() { return !!fatto; }, el: d };
  }
  function titoletto(parent, testo) {
    const p = typeof parent === "string" ? $(parent) : parent || $("#pannello");
    const h = document.createElement("h2"); h.textContent = testo; p.appendChild(h); return h;
  }
  let passoEl = null;
  function didascalia(testo) {
    const f = $("#didascalia"); if (!f) return;
    let t = f.querySelector(".testo"); if (!t) { t = document.createElement("span"); t.className = "testo"; f.appendChild(t); }
    t.innerHTML = testo; tex(t);
  }
  function animazione(fn, parent) {
    let attiva = false, t = 0, last = null, id = null;
    const frame = ts => { if (!attiva) return; const dt = last == null ? 0 : Math.min((ts - last) / 1000, 0.05);
      last = ts; t += dt; fn(dt, t); id = requestAnimationFrame(frame); };
    const ctl = {
      play() { if (attiva) return; attiva = true; last = null; btn.textContent = "❚❚ Pausa"; id = requestAnimationFrame(frame); },
      pausa() { attiva = false; btn.textContent = "▶ Play"; if (id) cancelAnimationFrame(id); },
      reset() { t = 0; fn(0, 0); },
      passo(dt = 1 / 60) { t += dt; fn(dt, t); },
      get attiva() { return attiva; }, get t() { return t; }
    };
    const btn = bottone(parent, "▶ Play", () => (attiva ? ctl.pausa() : ctl.play()), true);
    return ctl;
  }
  function guida(passi) {
    let i = 0;
    const f = $("#didascalia");
    didascalia("");  // crea lo span del testo prima dei bottoni
    passoEl = document.createElement("span"); passoEl.className = "passo"; f.prepend(passoEl);
    const nav = document.createElement("span"); nav.style.marginLeft = "auto"; nav.className = "doll-riga";
    const ind = document.createElement("button"); ind.className = "doll-btn"; ind.textContent = "← Indietro";
    const av = document.createElement("button"); av.className = "doll-btn primario"; av.textContent = "Avanti →";
    nav.append(ind, av); f.appendChild(nav);
    const vai = k => { i = Math.max(0, Math.min(passi.length - 1, k)); passoEl.textContent = `${i + 1}/${passi.length}`;
      didascalia(passi[i].testo); passi[i].applica && passi[i].applica(); ind.disabled = i === 0; av.disabled = i === passi.length - 1; };
    ind.onclick = () => vai(i - 1); av.onclick = () => vai(i + 1);
    vai(0);
    // ogni passo e' anche uno stato per il controllo automatico
    window.dollStati = (window.dollStati || []).concat(passi.map((p, k) => ({ nome: `passo ${k + 1}`, applica: () => vai(k) })));
    return { vai, get indice() { return i; } };
  }
  function stati(lista) { window.dollStati = (window.dollStati || []).concat(lista); }
  function pronto() { tex(document.body); window.dollPronto = true; }
  // dimensioni della vista (per canvas e Plotly)
  function vista() { const v = $("#vista"); return { el: v, w: v.clientWidth, h: v.clientHeight }; }
  function canvas(dpr = window.devicePixelRatio || 1) {
    const v = $("#vista"), c = document.createElement("canvas"); v.appendChild(c);
    const ctx = c.getContext("2d");
    const fit = () => { c.width = v.clientWidth * dpr; c.height = v.clientHeight * dpr;
      c.style.width = v.clientWidth + "px"; c.style.height = v.clientHeight + "px"; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); };
    fit(); window.addEventListener("resize", fit);
    if (window.ResizeObserver) new ResizeObserver(fit).observe(v);
    return { c, ctx, get w() { return v.clientWidth; }, get h() { return v.clientHeight; }, fit };
  }
  window.Doll = { slider, scelta, bottone, interruttore, dati, lettura, bersaglio, titoletto, didascalia, animazione, guida, stati, pronto, tex, col, ruolo, vista, canvas };
})();
