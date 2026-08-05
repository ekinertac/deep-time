/*
 * page.js: builds every piece of content from data.js and wires the scroll.
 *
 * Responsibilities, in order:
 *   1. render()   - the descent (20 century panels + the beats and image plates
 *                   interleaved between them), the right-hand tick rail, the three
 *                   regime cards, the source list.
 *   2. mirror()   - the payoff chart: population above the axis, months-alive-and-
 *                   free below it, so the anti-correlation is one shape.
 *   3. track()    - a rAF loop that turns scroll position into a continuous
 *                   century coordinate `t` (0..19), updates the readout and the
 *                   rail, and publishes it on window.RomeState for scene.js.
 *
 * scene.js is a consumer of RomeState and nothing else; if WebGL is unavailable it
 * simply never loads and every line above still runs. No library, no build step.
 *
 * Read alongside: data.js (all figures), site.css (the classes toggled here).
 */
(function () {
  'use strict';

  var reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Shared state, read by scene.js each frame. */
  window.RomeState = { t: 0, i: 0, reduced: reduced };

  /* ---------- schematic depth ----------
   * Rome's low-lying centre rose by up to about nine metres in two thousand years,
   * but not steadily: most of the fill is post-antique debris and Tiber silt, and
   * the hills barely moved. This curve is a smooth stand-in for that: deposition
   * weighted toward the middle centuries. It is a diagram, and the closing section
   * says so.
   */
  var DEPTH = (function () {
    var w = [], i, cum = 0, total = 0, out = [];
    for (i = 0; i < 20; i++) { w[i] = 0.5 + Math.exp(-Math.pow((i - 9) / 6.5, 2)); total += w[i]; }
    for (i = 0; i < 20; i++) { out[i] = -9 * (1 - cum / total); cum += w[i]; }
    return out;
  })();

  /* ---------- helpers ---------- */
  function human(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(n % 1000000 === 0 ? 0 : 1).replace('.0', '') + 'M';
    if (n >= 1000) return Math.round(n / 1000) + 'k';
    return String(n);
  }
  function popText(c) { return human(c.pop[0]) + ' – ' + human(c.pop[1]); }
  function verdictText(c) {
    if (c.free >= 999) return 'a lifetime';
    if (c.free < 2) return 'weeks';
    if (c.free < 18) return Math.round(c.free) + ' months';
    if (c.free < 600) return 'years';
    return 'a lifetime';
  }
  /* Geometric midpoint: on a log axis this is the honest centre of a range. */
  function popMid(c) { return Math.sqrt(c.pop[0] * c.pop[1]); }
  function freePlot(c) { return c.free >= 999 ? 420 : c.free; }

  /* ---------- 1. render ---------- */
  function centHTML(c) {
    return '<section class="cent band-' + c.band + '" id="c' + c.n + '" data-i="' + (c.n - 1) + '">' +
      '<div class="cent__ghost" aria-hidden="true">' + c.roman + '</div>' +
      '<article class="cent__body">' +
        '<div class="cent__head"><span class="cent__num">' + c.roman + '</span>' +
        '<span class="cent__yrs">' + c.years + '</span></div>' +
        '<h2 class="cent__title">' + c.title + '</h2>' +
        '<div class="cent__meta">' +
          '<div><span class="k">inhabitants</span><span class="v">' + popText(c) + '</span></div>' +
          '<div><span class="k">you stay free for</span><span class="v band">' + verdictText(c) + '</span></div>' +
        '</div>' +
        '<p class="cent__pop">' + c.popNote + '</p>' +
        c.body.map(function (p) { return '<p>' + p + '</p>'; }).join('') +
        '<p class="cent__danger"><b>what actually kills you here</b>' + c.danger + '</p>' +
        '<p class="cent__ends">' + c.ends + '</p>' +
      '</article></section>';
  }

  // alt text goes into an attribute, so quotes and angle brackets have to die.
  function esc(t) {
    return String(t).replace(/&/g, '&amp;').replace(/"/g, '&quot;')
                    .replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function beatHTML(b) {
    if (b.kind === 'door') {
      // Full-bleed, full-height, and the only thing on screen when it is on
      // screen. The city model is wide, cold and abstract; a door is close,
      // material and in reach, which is the whole reason it interrupts.
      return '<section class="door" id="door-' + b.key + '">' +
        '<img class="door__img" src="' + b.src + '" alt="' + esc(b.what) + '"' +
        ' width="1920" height="1080" loading="lazy" decoding="async">' +
        '<div class="door__text"><p class="door__word">' + b.word + '</p>' +
        '<p class="door__ask">' + b.ask + '</p>' +
        '<p class="door__cap">' + b.cap + '</p></div></section>';
    }
    if (b.kind === 'plate') {
      return '<div class="plate"><figure>' +
        '<img class="plate__img" src="' + b.src + '" alt="' + esc(b.what) + '"' +
        ' width="1920" height="1080" loading="lazy" decoding="async">' +
        '<figcaption>' + b.cap + '</figcaption></figure></div>';
    }
    return '<section class="beat' + (b.quiet ? ' beat--quiet' : '') + '">' +
      '<p class="beat__yr">' + b.yr + '</p><h2 class="beat__h">' + b.h + '</h2><p>' + b.p + '</p></section>';
  }

  function render() {
    var out = [];
    /* after:0 means "before the first century", which the loop below cannot
       express because it hangs interludes off the century they follow. */
    BEATS.filter(function (b) { return b.after === 0; }).forEach(function (b) { out.push(beatHTML(b)); });
    CENTURIES.forEach(function (c) {
      out.push(centHTML(c));
      BEATS.filter(function (b) { return b.after === c.n; }).forEach(function (b) { out.push(beatHTML(b)); });
    });
    document.getElementById('descent').innerHTML = out.join('');

    /* Rail: tick length encodes months alive and free, so navigation is also the
       survival chart. Log-scaled, because the range is 1 month to a lifetime. */
    document.getElementById('rail').innerHTML = CENTURIES.map(function (c) {
      var w = 8 + 30 * (Math.log10(freePlot(c)) / Math.log10(420));
      return '<a class="rail__t band-' + c.band + '" href="#c' + c.n + '" data-r="' + c.roman + '" ' +
        'data-i="' + (c.n - 1) + '" style="--w:' + w.toFixed(1) + 'px" ' +
        'aria-label="Century ' + c.roman + ', ' + c.years + ', you stay free ' + verdictText(c) + '"></a>';
    }).join('');

    document.getElementById('regimes').innerHTML = REGIMES.map(function (r) {
      return '<div class="reg" style="--rw:' + r.colour + '">' +
        '<span class="reg__w">' + r.word + '</span>' +
        '<span class="reg__span">centuries ' + CENTURIES[r.from - 1].roman + ' – ' + CENTURIES[r.to - 1].roman + '</span>' +
        '<p class="reg__ask">&ldquo;' + r.ask + '&rdquo;</p>' +
        '<p>' + r.line + '</p></div>';
    }).join('');

    var srcEl = document.getElementById('sources');
    if (srcEl) {
      srcEl.innerHTML = SOURCES.map(function (s) {
        return '<li><a href="' + s[1] + '" rel="noopener">' + s[0] + '</a></li>';
      }).join('');
    }
  }

  /* A door is a full-screen interruption, so the instruments step out of its
     way. Without this the fixed readout sits on top of the door's caption, and
     the rail ticks compete with a photograph that is meant to stop the scroll. */
  function doorWatch() {
    var doors = document.querySelectorAll('.door');
    if (!doors.length || !('IntersectionObserver' in window)) return;
    /* A set, not a counter: the observer's first callback reports every element,
       including the ones off screen, so counting would start at minus three. */
    var open = [];
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var i = open.indexOf(e.target);
        if (e.isIntersecting && i < 0) open.push(e.target);
        if (!e.isIntersecting && i >= 0) open.splice(i, 1);
      });
      document.body.classList.toggle('in-door', open.length > 0);
    }, { threshold: 0.55 });
    doors.forEach(function (d) { io.observe(d); });
  }

  /* ---------- 2. the mirror chart ---------- */
  function mirror() {
    var svg = document.getElementById('mirror');
    if (!svg) return;
    var W = 1000, H = 470, AX = 236, L = 46, R = 968, G = 17;   // G: gutter for the century labels
    var x = function (i) { return L + (R - L) * (i / 19); };

    var pLo = Math.log10(12000), pHi = Math.log10(3000000);
    var py = function (v) { return (AX - G) - 8 - 176 * ((Math.log10(v) - pLo) / (pHi - pLo)); };
    var fy = function (v) { return (AX + G) + 186 * (Math.log10(v) / Math.log10(420)); };

    var top = CENTURIES.map(function (c, i) { return (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + py(popMid(c)).toFixed(1); }).join(' ');
    var area = top + ' L' + x(19) + ' ' + (AX - G) + ' L' + x(0) + ' ' + (AX - G) + ' Z';

    /* One column per century below the axis. Discrete, because the survival figure
       is a judgement per century and not a continuous series; the population above
       is a curve, because it is. */
    var bars = CENTURIES.map(function (c, i) {
      var w = (R - L) / 19 * 0.6, bx = x(i) - w / 2;
      /* Floor of 7px so the one 'weeks' century is a mark and not an absence. */
      var y2 = Math.max(fy(freePlot(c)), AX + G + 7);
      var forever = c.free >= 999;
      return '<rect x="' + bx.toFixed(1) + '" y="' + (AX + G) + '" width="' + w.toFixed(1) +
        '" height="' + (y2 - AX - G).toFixed(1) + '" fill="var(--b-' + c.band + ')" opacity="0.92"/>' +
        (forever ? '<path d="M' + bx.toFixed(1) + ' ' + (y2 - 6).toFixed(1) + ' l' + w.toFixed(1) +
          ' -8 M' + bx.toFixed(1) + ' ' + (y2 - 1).toFixed(1) + ' l' + w.toFixed(1) + ' -8" ' +
          'stroke="#0a0806" stroke-width="2.5" fill="none"/>' : '');
    }).join('');

    var ticks = CENTURIES.map(function (c, i) {
      return '<text x="' + x(i).toFixed(1) + '" y="' + AX + '" class="mx">' + c.roman + '</text>';
    }).join('');

    svg.setAttribute('viewBox', '0 0 ' + W + ' ' + H);
    svg.innerHTML =
      '<defs><linearGradient id="pg" x1="0" y1="0" x2="0" y2="1">' +
      '<stop offset="0%" stop-color="#c79a44" stop-opacity="0.4"/>' +
      '<stop offset="100%" stop-color="#c79a44" stop-opacity="0.03"/></linearGradient></defs>' +
      '<path d="' + area + '" fill="url(#pg)"/>' +
      '<path d="' + top + '" fill="none" stroke="#c79a44" stroke-width="2.5" stroke-linejoin="round"/>' +
      bars +
      '<line x1="' + L + '" y1="' + AX + '" x2="' + R + '" y2="' + AX + '" stroke="rgba(236,226,205,0.28)" stroke-width="1"/>' +
      ticks +
      '<text x="' + (x(0) + 4) + '" y="' + (py(725000) - 14) + '" class="mn">≈1 million, disputed</text>' +
      '<text x="' + x(13) + '" y="' + (py(21000) - 28) + '" class="mn" text-anchor="middle">15,000–17,000</text>' +
      '<line x1="' + x(13) + '" y1="' + (py(21000) - 22) + '" x2="' + x(13) + '" y2="' + (py(21000) - 6) + '" stroke="rgba(236,226,205,0.3)"/>' +
      '<text x="' + (x(19) + 2) + '" y="' + (py(2805109) - 14) + '" class="mn" text-anchor="end">2.8 million</text>' +
      '<text x="' + x(9) + '" y="' + (fy(420) + 24) + '" class="mn" text-anchor="middle">the rest of your life ↓</text>' +
      '<text x="' + x(5) + '" y="' + (fy(1) + 20) + '" class="mn" text-anchor="middle">weeks</text>';
  }

  /* ---------- 3. scroll tracking ---------- */
  function track() {
    var panels = [].slice.call(document.querySelectorAll('.cent'));
    var rails = [].slice.call(document.querySelectorAll('.rail__t'));
    var hud = document.getElementById('hud'), rail = document.getElementById('rail');
    var city = document.getElementById('city');
    var el = {
      c: document.getElementById('hud-c'), y: document.getElementById('hud-y'),
      p: document.getElementById('hud-p'), d: document.getElementById('hud-d'),
      v: document.getElementById('hud-v')
    };
    var centers = [], last = -1, ticking = false;

    function measure() {
      centers = panels.map(function (p) {
        var r = p.getBoundingClientRect();
        return r.top + scrollY + r.height / 2;
      });
    }

    function frame() {
      ticking = false;
      if (!centers.length) return;
      var mid = scrollY + innerHeight * 0.5, t;

      if (mid <= centers[0]) t = 0;
      else if (mid >= centers[19]) t = 19;
      else {
        var k = 0;
        while (k < 19 && mid > centers[k + 1]) k++;
        t = k + (mid - centers[k]) / (centers[k + 1] - centers[k]);
      }
      RomeState.t = t;
      var i = Math.max(0, Math.min(19, Math.round(t)));
      RomeState.i = i;
      /* On the gate the reading column is on the left, so the model has to move to
         the right; below it the column moves right and the model moves back. */
      RomeState.hero = Math.max(0, Math.min(1, 1 - scrollY / (innerHeight * 0.75)));

      /* HUD visibility: only while the descent is on screen. */
      var inDescent = mid > centers[0] - innerHeight && mid < centers[19] + innerHeight;
      hud.classList.toggle('on', inDescent);
      rail.classList.toggle('on', inDescent);
      if (city) city.classList.toggle('dim', mid > centers[19] + innerHeight * 0.5);

      if (i !== last) {
        last = i;
        var c = CENTURIES[i];
        hud.className = 'hud band-' + c.band + (inDescent ? ' on' : '');
        el.c.textContent = c.roman;
        el.y.textContent = c.years;
        el.p.textContent = popText(c);
        el.d.textContent = DEPTH[i].toFixed(1).replace('-', '−') + ' m';
        el.v.textContent = verdictText(c);
        rails.forEach(function (r, j) { r.classList.toggle('is-live', j === i); });
        panels.forEach(function (p, j) { p.classList.toggle('is-live', j === i); });
      }
    }

    function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }

    measure();
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', function () { measure(); onScroll(); });
    /* Fonts land late and move everything; re-measure when they do. */
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measure(); onScroll(); });
    setTimeout(function () { measure(); onScroll(); }, 400);
    onScroll();
  }

  render();
  doorWatch();
  mirror();
  track();
})();
