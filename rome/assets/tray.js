/*
 * tray.js: the finds tray, this episode's lightbox for the five image plates.
 *
 * The conceit: a plate is a find. Clicking one lifts it out of the strata and
 * onto an examination surface: the page dims to a closed dig house, the image
 * is uncovered top-to-bottom under one pass of raking light, and around it sit
 * the instruments of an excavation record: registration corner marks, a
 * catalogue tag (plate numeral, the century it follows, street depth from the
 * page's own depth curve), a minium-and-ink ranging-rod scale bar that states
 * the honest pixel scale, and a loupe that follows the pointer at 1:1. The
 * bottom edge is the finds register: five Cinzel numerals, tick-styled like
 * the rail, for moving between plates.
 *
 * Scope is the five .plate figures only; the three full-screen doors are not
 * zoomable and are untouched. Built on native <dialog> for the focus trap,
 * Esc, inert background and focus-return, all of which are easy to get wrong
 * by hand. Deliberately shares nothing with episode 01's lightbox: every
 * episode owns its own look.
 *
 * Depends on: data.js (BEATS/CENTURIES globals), page.js (renders the
 * .plate__open triggers and publishes RomeState.depth). Styling lives in
 * site.css under "the finds tray". No library, no build step, no rAF loop:
 * everything here is event-driven, so the page stays quiet when idle.
 */
(function () {
  'use strict';

  /* data.js declares BEATS/CENTURIES with const, so they are script-scope
     globals and never properties of window: test with typeof, not window. */
  if (typeof HTMLDialogElement === 'undefined' || typeof BEATS === 'undefined') return;

  var plates = BEATS.filter(function (b) { return b.kind === 'plate'; });
  var triggers = [].slice.call(document.querySelectorAll('.plate__open'));
  /* Same source, same filter, same order as page.js's render loop for plates
     (doors interleave in the DOM but not in this filtered list), so index n in
     `triggers` is index n in `plates`. Bail out rather than mislabel if that
     ever stops being true. */
  if (!plates.length || triggers.length !== plates.length) return;

  var fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
  var ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];
  var LOUPE = 190;   // loupe diameter, must match .tray__loupe in site.css

  /* ---------- the dialog ---------- */
  var dlg = document.createElement('dialog');
  dlg.className = 'tray';
  dlg.innerHTML =
    '<div class="tray__head">' +
      '<span class="tray__plate"><span class="tray__pl">Plate</span> <span class="tray__pn"></span></span>' +
      '<span class="tray__meta"></span>' +
      '<button class="tray__close" type="button">esc &middot; close</button>' +
    '</div>' +
    '<div class="tray__stage">' +
      '<span class="tray__frame">' +
        '<img class="tray__img" alt="">' +
        '<span class="marks" aria-hidden="true"></span>' +
        '<span class="tray__sweep" aria-hidden="true"></span>' +
        '<span class="tray__loupe" aria-hidden="true"><span class="tray__lscale">1 : 1</span></span>' +
      '</span>' +
    '</div>' +
    '<div class="tray__foot">' +
      '<div class="tray__bar"><span class="tray__ruler" aria-hidden="true">' +
        '<i></i><i></i><i></i><i></i></span>' +
      '<span class="tray__px"></span></div>' +
      '<p class="tray__what"></p>' +
      '<p class="tray__cap"></p>' +
      '<nav class="tray__reg" aria-label="Finds register: all plates"></nav>' +
    '</div>';
  document.body.appendChild(dlg);

  var img = dlg.querySelector('.tray__img');
  var frame = dlg.querySelector('.tray__frame');
  var loupe = dlg.querySelector('.tray__loupe');
  var el = {
    pn: dlg.querySelector('.tray__pn'),
    meta: dlg.querySelector('.tray__meta'),
    what: dlg.querySelector('.tray__what'),
    cap: dlg.querySelector('.tray__cap'),
    ruler: dlg.querySelector('.tray__ruler'),
    px: dlg.querySelector('.tray__px'),
    reg: dlg.querySelector('.tray__reg')
  };

  el.reg.innerHTML = plates.map(function (b, n) {
    return '<button type="button" data-n="' + n + '" aria-label="Plate ' + ROMAN[n] + '">' + ROMAN[n] + '</button>';
  }).join('');
  var regBtns = [].slice.call(el.reg.querySelectorAll('button'));

  var cur = 0;

  /* ---------- catalogue tag ---------- */
  function metaFor(b) {
    var c = CENTURIES[b.after - 1];
    var d = (window.RomeState && RomeState.depth) ? RomeState.depth[b.after - 1] : null;
    return 'after cent. ' + c.roman + ' · ' + c.years +
      (d == null ? '' : ' · streets at ' + d.toFixed(1).replace('-', '−') + ' m');
  }

  /* The scale bar is a ranging rod for pixels: its length is a quarter of the
     source width at the current display scale, so the label can say honestly
     how much of the file the screen is showing. */
  function setRuler() {
    var w = img.clientWidth, nw = img.naturalWidth;
    if (!w || !nw) return;
    el.ruler.style.width = (w / 4).toFixed(0) + 'px';
    el.px.textContent = Math.round(nw / 4) + ' px of ' + nw + ' · shown at ' +
      Math.round(w / nw * 100) + '%' + (fine ? ' · loupe 1:1' : '');
  }

  /* ---------- showing a plate ---------- */
  function show(n) {
    cur = (n + plates.length) % plates.length;
    var b = plates[cur];
    el.pn.textContent = ROMAN[cur];
    el.meta.textContent = metaFor(b);
    el.what.textContent = b.what;
    el.cap.innerHTML = b.cap;              // caption carries markup (<i>) in data.js
    img.alt = b.what;
    dlg.setAttribute('aria-label', 'Plate ' + ROMAN[cur] + ': ' + b.what);
    regBtns.forEach(function (r, j) {
      if (j === cur) r.setAttribute('aria-current', 'true');
      else r.removeAttribute('aria-current');
    });
    loupe.style.backgroundImage = 'url("' + b.src + '")';
    if (img.getAttribute('src') !== b.src) {
      img.classList.add('is-swap');
      img.src = b.src;                     // 'load' fires even from cache
    } else {
      setRuler();
    }
  }
  img.addEventListener('load', function () {
    img.classList.remove('is-swap');
    setRuler();
  });

  function open(n) {
    show(n);
    document.documentElement.classList.add('tray-open');
    dlg.showModal();
    /* Re-arm the uncovering animation on every open. */
    dlg.classList.remove('is-open');
    void dlg.offsetWidth;
    dlg.classList.add('is-open');
    setRuler();
  }

  dlg.addEventListener('close', function () {
    document.documentElement.classList.remove('tray-open');
    dlg.classList.remove('is-open');
  });

  /* ---------- the loupe ----------
   * Pointer-driven only: no animation frame, no work while the hand is still.
   * The background image is the same file the <img> shows, drawn at natural
   * size, so what is inside the ring is the actual pixels of the plate.
   */
  if (fine) {
    frame.addEventListener('pointermove', function (e) {
      var r = img.getBoundingClientRect();
      var x = e.clientX - r.left, y = e.clientY - r.top;
      if (x < 0 || y < 0 || x > r.width || y > r.height) {
        frame.classList.remove('has-loupe');
        return;
      }
      frame.classList.add('has-loupe');
      loupe.style.left = x + 'px';
      loupe.style.top = y + 'px';
      loupe.style.backgroundSize = img.naturalWidth + 'px ' + img.naturalHeight + 'px';
      loupe.style.backgroundPosition =
        (LOUPE / 2 - x / r.width * img.naturalWidth) + 'px ' +
        (LOUPE / 2 - y / r.height * img.naturalHeight) + 'px';
    });
    frame.addEventListener('pointerleave', function () {
      frame.classList.remove('has-loupe');
    });
  }

  /* ---------- wiring ---------- */
  triggers.forEach(function (t, n) {
    t.addEventListener('click', function () { open(n); });
  });
  regBtns.forEach(function (r) {
    r.addEventListener('click', function () { show(+r.dataset.n); });
  });
  dlg.querySelector('.tray__close').addEventListener('click', function () { dlg.close(); });
  /* Clicking the dark around the plate closes. The dialog spans the viewport
     width, so "the dark" is the dialog element itself plus the bare rows
     around the frame; the image itself never closes, because it hosts the
     loupe and an accidental dismiss there is easy. */
  dlg.addEventListener('click', function (e) {
    var t = e.target;
    if (t === dlg || t.classList.contains('tray__stage') ||
        t.classList.contains('tray__head') || t.classList.contains('tray__foot')) dlg.close();
  });
  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(cur - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(cur + 1); }
  });
  addEventListener('resize', function () { if (dlg.open) setRuler(); });
})();
