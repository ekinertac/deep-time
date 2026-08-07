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
  /* Loupe geometry and magnification. The diameter is pushed into CSS as a
     custom property rather than duplicated there, because the offset maths below
     depends on it and the two drifting apart is a silent bug. */
  var LOUPE = 300;          // diameter in px
  var ZOOM_MIN = 0.5;       // below 1 the loupe shows more of the plate, not less
  var ZOOM_MAX = 8;
  var zoom = 1;             // 1 = the plate's actual pixels, 1:1
  var lastX = null, lastY = null;

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
      Math.round(w / nw * 100) + '%' +
      // The loupe carries its own ratio, which changes with the wheel, so the
      // ruler must not also claim one or the two disagree the moment you zoom.
      (fine ? ' · scroll on the loupe to magnify' : '');
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
    zoom = 1;
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
      lastX = x; lastY = y;
      place(r);
    });
    frame.addEventListener('pointerleave', function () {
      frame.classList.remove('has-loupe');
    });

    /* Scroll to change magnification. Multiplicative, so each notch feels the
       same at every zoom, and preventDefault because the wheel would otherwise
       scroll the tray out from under the hand. */
    frame.addEventListener('wheel', function (e) {
      if (!frame.classList.contains('has-loupe')) return;
      e.preventDefault();
      var step = Math.exp(-e.deltaY * 0.0015);
      zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, zoom * step));
      place(img.getBoundingClientRect());
    }, { passive: false });
  }

  /* Draw the loupe at the last known pointer position and current zoom. The
     background is the plate's own file at natural size times the zoom, so what
     is inside the ring really is the plate's pixels rather than an upscale of
     what the page is showing. */
  function place(r) {
    if (lastX === null) return;
    var w = img.naturalWidth * zoom, h = img.naturalHeight * zoom;
    loupe.style.setProperty('--loupe-d', LOUPE + 'px');
    loupe.style.left = lastX + 'px';
    loupe.style.top = lastY + 'px';
    loupe.style.backgroundSize = w + 'px ' + h + 'px';
    loupe.style.backgroundPosition =
      (LOUPE / 2 - lastX / r.width * w) + 'px ' +
      (LOUPE / 2 - lastY / r.height * h) + 'px';
    var lbl = loupe.querySelector('.tray__lscale');
    if (lbl) lbl.textContent = zoom >= 0.995 && zoom <= 1.005
      ? '1 : 1'
      : (zoom < 1 ? '1 : ' + (1 / zoom).toFixed(1) : zoom.toFixed(1) + ' : 1');
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
