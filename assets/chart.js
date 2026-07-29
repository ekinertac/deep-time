/*
 * chart.js — renders the three-panel deep-time chart and its shared interactions.
 *
 * Structure: three stacked single-series panels (oxygen, CO₂, temperature) over
 * ONE shared x-axis. They are separate plots on purpose — three quantities of
 * this range cannot share a y-axis, and a second y-scale on one plot would
 * manufacture a correlation the data does not contain.
 *
 * The x-axis carries an explicit scale break at 539 Ma. A linear 4.54 Gyr axis
 * compresses the entire Phanerozoic — every era with a survival time longer than
 * a minute — into the last 12% of the width. The break gives the Precambrian 42%
 * and the Phanerozoic 58%, and is drawn and labelled so the reader can see the
 * compression is deliberate. Every series is split into two paths at the break so
 * no line is ever drawn across it.
 *
 * GEOMETRY vs TEXT: the SVG is stretched to the container with
 * preserveAspectRatio="none", which scales x and y by different factors. That is
 * fine for paths (strokes are held true with vector-effect) but it visibly
 * distorts glyphs. So the SVG carries ONLY geometry, and every label is an
 * absolutely positioned HTML element in a sibling layer, placed with percentages
 * off the same scales. Text then stays undistorted, selectable and in rem units.
 *
 * Depends on assets/curves.js (PANELS) and assets/data.js (ERAS, formatAge,
 * eraFile). Styling in assets/chart.css; markup contract in chart.html.
 */

(function () {
  const root = document.getElementById('chart');
  if (!root) return;

  const BREAK = 539;          // Ma — Precambrian / Phanerozoic, where the axis splits
  const SPAN = 4540;
  const W = 1000;             // viewBox units
  const PAD_L = 54, PAD_R = 14;
  const PLOT_W = W - PAD_L - PAD_R;
  const GAP = 18;             // width of the break marker
  const A_W = (PLOT_W - GAP) * 0.42;   // Precambrian zone
  const B_W = (PLOT_W - GAP) * 0.58;   // Phanerozoic zone
  const A_X = PAD_L;
  const B_X = PAD_L + A_W + GAP;
  const H = 100;              // panel viewBox height; CSS sets the rendered height

  /* ---- scales ---- */
  const x = (age) =>
    age >= BREAK
      ? A_X + ((SPAN - age) / (SPAN - BREAK)) * A_W
      : B_X + ((BREAK - age) / BREAK) * B_W;

  const ageAt = (px) => {
    if (px <= A_X + A_W) return SPAN - ((px - A_X) / A_W) * (SPAN - BREAK);
    if (px >= B_X) return BREAK - ((px - B_X) / B_W) * BREAK;
    return BREAK;
  };

  const yScale = (p) => {
    if (p.scale === 'log') {
      const lo = Math.log10(p.min), hi = Math.log10(p.max);
      return (v) => H - ((Math.log10(Math.max(v, p.min)) - lo) / (hi - lo)) * H;
    }
    return (v) => H - ((v - p.min) / (p.max - p.min)) * H;
  };

  /* Percentages, for placing HTML labels over the stretched SVG. */
  const xPct = (age) => (x(age) / W) * 100;
  const yPct = (v, y) => (y(v) / H) * 100;

  /* ---- helpers ---- */
  const seg = (data, lo, hi) => data.filter(([a]) => a >= lo && a <= hi);
  const path = (pts, y) => pts.map(([a, v], i) => (i ? 'L' : 'M') + x(a).toFixed(1) + ' ' + y(v).toFixed(2)).join(' ');
  const area = (pts, y) =>
    pts.length ? path(pts, y) + ` L${x(pts[pts.length - 1][0]).toFixed(1)} ${H} L${x(pts[0][0]).toFixed(1)} ${H} Z` : '';

  function valueAt(data, age) {
    if (age >= data[0][0]) return data[0][1];
    if (age <= data[data.length - 1][0]) return data[data.length - 1][1];
    for (let i = 0; i < data.length - 1; i++) {
      const [a1, v1] = data[i], [a2, v2] = data[i + 1];
      if (age <= a1 && age >= a2) return v1 + (v2 - v1) * ((a1 - age) / (a1 - a2));
    }
    return null;
  }

  const eraAt = (age) => ERAS.find((e) => age <= e.from && age > e.to) || ERAS[ERAS.length - 1];

  /* The scale-break marker. Rendered once per plot and once over the axis rather
     than as a single overlay across the whole stack — a stack-wide overlay also
     covers the panel headings and paints out whichever letter falls under it. */
  const breakMark = () =>
    `<div class="c-break" style="left:${(((A_X + A_W) / W) * 100).toFixed(3)}%;width:${((GAP / W) * 100).toFixed(3)}%"></div>`;

  /* ---- one panel ---- */
  function panel(p) {
    const y = yScale(p);
    const pre = seg(p.data, BREAK, SPAN);
    const post = seg(p.data, 0, BREAK);

    const gridLines = p.ticks
      .map(
        (t) =>
          `<line class="c-grid" x1="${PAD_L}" x2="${(A_X + A_W).toFixed(1)}" y1="${y(t).toFixed(2)}" y2="${y(t).toFixed(2)}"/>
           <line class="c-grid" x1="${B_X.toFixed(1)}" x2="${W - PAD_R}" y1="${y(t).toFixed(2)}" y2="${y(t).toFixed(2)}"/>`
      )
      .join('');

    const yLabels = p.ticks
      .map(
        (t) =>
          `<span class="c-ytick" style="top:${yPct(t, y).toFixed(2)}%;left:0">${
            p.scale === 'log' && t >= 1000 ? t / 1000 + 'k' : t
          }</span>`
      )
      .join('');

    // The threshold label sits at the LEFT edge of the plot, above its rule, so it
    // never collides with the curve — which runs high on the right in every panel.
    const ruleLabel = `<span class="c-rulelabel" style="top:${yPct(p.rule.at, y).toFixed(2)}%;left:${((PAD_L + 6) / W) * 100}%">${p.rule.label}</span>`;

    return `
      <div class="c-panel">
        <div class="c-head">
          <h3 class="c-title"><i style="background:${p.color}"></i>${p.title}</h3>
          <span class="c-unit">${p.unit}</span>
          <span class="c-rulenote">${p.rule.label}</span>
        </div>
        <div class="c-plot">
          ${breakMark()}
          <svg class="c-svg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img"
               aria-label="${p.title} across 4.54 billion years, in ${p.unit}. The same values are in the table below.">
            ${gridLines}
            <path class="c-area" d="${area(pre, y)}" fill="${p.color}"/>
            <path class="c-area" d="${area(post, y)}" fill="${p.color}"/>
            <line class="c-rule" x1="${PAD_L}" x2="${W - PAD_R}" y1="${y(p.rule.at).toFixed(2)}" y2="${y(p.rule.at).toFixed(2)}"/>
            <path class="c-line" d="${path(pre, y)}" stroke="${p.color}"/>
            <path class="c-line" d="${path(post, y)}" stroke="${p.color}"/>
            <line class="c-cross" data-cross="${p.key}" y1="0" y2="${H}" style="display:none"/>
          </svg>
          <div class="c-labels">
            ${yLabels}${ruleLabel}
            <span class="c-dot" data-dot="${p.key}" style="background:${p.color};display:none"></span>
          </div>
        </div>
      </div>`;
  }

  /* ---- shared x-axis: ticks and the era strip, both plain HTML ---- */
  function axis() {
    // `opt` marks the ticks that are dropped on narrow screens, where the full
    // set collides — particularly either side of the scale break. They are
    // rendered and hidden by CSS rather than re-rendered on resize.
    const ticks = [
      [4500, '4.5 Ga', 0], [4000, '4.0', 1], [3000, '3.0', 0], [2000, '2.0', 1], [1000, '1.0', 0],
      [500, '500 Ma', 0], [400, '400', 1], [300, '300', 0], [200, '200', 1], [100, '100', 0], [0, 'now', 0],
    ]
      .map(([a, l, opt]) => `<span class="c-xtick"${opt ? ' data-opt' : ''} style="left:${xPct(a).toFixed(2)}%">${l}</span>`)
      .join('');

    // Era identity is carried by text, never by colour. The label text itself is
    // chosen after layout by fitStripLabels() — guessing from the percentage
    // width clips long names, and a half-rendered word is worse than none.
    const strip = ERAS.map((e) => {
      const l = xPct(e.from), w = xPct(e.to) - l;
      return `<a class="c-era" href="${eraFile(e)}" title="${e.name} — ${e.verdict}" data-name="${e.name}"
                 style="left:${l.toFixed(2)}%;width:${Math.max(w - 0.12, 0.3).toFixed(2)}%"><span></span></a>`;
    }).join('');

    return `<div class="c-axis">${breakMark()}<div class="c-xticks">${ticks}</div><div class="c-strip">${strip}</div></div>`;
  }

  /* ---- render ---- */
  root.innerHTML =
    `<div class="c-stack">
       ${PANELS.map(panel).join('')}
       ${axis()}
     </div>
     <div class="c-readout" id="c-readout" hidden>
       <span class="c-r-age" id="c-r-age"></span>
       <a class="c-r-era" id="c-r-era" href="#"></a>
       <span class="c-r-vals" id="c-r-vals"></span>
     </div>`;

  /* Choose each era label AFTER layout, from the box it actually got. A name is
     shown whole or not at all — a clipped word reads as a typo, and the full name
     is always available from the title attribute and the table below. */
  function fitStripLabels() {
    root.querySelectorAll('.c-era').forEach((a) => {
      const span = a.firstElementChild;
      const name = a.dataset.name;
      const room = a.clientWidth - 6;
      span.textContent = name;
      if (span.scrollWidth <= room) return;
      span.textContent = name.slice(0, 3);
      if (span.scrollWidth > room) span.textContent = '';
    });
  }
  fitStripLabels();
  addEventListener('resize', fitStripLabels);

  /* ---- table view: every value reachable without the pointer ---- */
  const tbody = document.getElementById('c-table');
  if (tbody) {
    tbody.innerHTML = ERAS.map((e) => {
      const a = e.from;
      return `<tr>
        <td><a href="${eraFile(e)}">${e.name}</a></td>
        <td>${formatAge(a)}</td>
        <td>${PANELS[0].fmt(valueAt(O2, a))}</td>
        <td>${a > 4000 ? '—' : PANELS[1].fmt(valueAt(CO2, a))}</td>
        <td>${a > 4000 ? '—' : PANELS[2].fmt(valueAt(TEMP, a))}</td>
        <td>${e.verdict}</td>
      </tr>`;
    }).join('');
  }

  /* ---- hover / focus: one crosshair across all three panels ---- */
  const stack = root.querySelector('.c-stack');
  const readout = document.getElementById('c-readout');
  const rAge = document.getElementById('c-r-age');
  const rEra = document.getElementById('c-r-era');
  const rVals = document.getElementById('c-r-vals');
  let cursorAge = null;

  function show(age) {
    cursorAge = Math.max(0, Math.min(SPAN, age));
    const px = xPct(cursorAge);
    const e = eraAt(cursorAge);

    PANELS.forEach((p) => {
      const y = yScale(p);
      const dot = root.querySelector(`[data-dot="${p.key}"]`);
      const cross = root.querySelector(`[data-cross="${p.key}"]`);
      const oldest = p.data[0][0];
      if (cursorAge > oldest) {           // off the left end of this series
        dot.style.display = 'none';
        cross.style.display = 'none';
        return;
      }
      const v = valueAt(p.data, cursorAge);
      dot.style.left = px.toFixed(2) + '%';
      dot.style.top = yPct(v, y).toFixed(2) + '%';
      dot.style.display = '';
      cross.setAttribute('x1', x(cursorAge).toFixed(1));
      cross.setAttribute('x2', x(cursorAge).toFixed(1));
      cross.style.display = '';
    });

    rAge.textContent = formatAge(cursorAge);
    rEra.textContent = e.name + ' · ' + e.verdict;
    rEra.href = eraFile(e);
    rVals.innerHTML = PANELS.map((p) => {
      const off = cursorAge > p.data[0][0];
      return `<span><i style="background:${p.color}"></i>${off ? 'off scale' : p.fmt(valueAt(p.data, cursorAge))}</span>`;
    }).join('');
    readout.hidden = false;
  }

  function hide() {
    readout.hidden = true;
    root.querySelectorAll('[data-dot],[data-cross]').forEach((n) => (n.style.display = 'none'));
    cursorAge = null;
  }

  const pointerAge = (ev) => {
    const r = stack.getBoundingClientRect();
    return ageAt(((ev.clientX - r.left) / r.width) * W);
  };

  stack.addEventListener('pointermove', (ev) => show(pointerAge(ev)));
  stack.addEventListener('pointerleave', hide);

  // Keyboard parity: the same values are reachable without a pointer.
  stack.tabIndex = 0;
  stack.setAttribute('role', 'application');
  stack.setAttribute('aria-label', 'Deep time chart. Arrow keys move the reading cursor through Earth history.');
  stack.addEventListener('focus', () => show(cursorAge == null ? 300 : cursorAge));
  stack.addEventListener('blur', hide);
  stack.addEventListener('keydown', (ev) => {
    if (cursorAge == null) return;
    // Step by a fraction of the zone the cursor is in, so both halves of the
    // broken axis move at a comfortable rate.
    const coarse = cursorAge >= BREAK ? 40 : 5;
    const step = ev.shiftKey ? coarse * 5 : coarse;
    if (ev.key === 'ArrowLeft') { show(cursorAge + step); ev.preventDefault(); }
    if (ev.key === 'ArrowRight') { show(cursorAge - step); ev.preventDefault(); }
    if (ev.key === 'Escape') { hide(); stack.blur(); }
  });
})();
