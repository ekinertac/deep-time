/*
 * roll.js — the "drop me somewhere" randomiser on the front page.
 *
 * The point is not novelty. Sampling a uniform random moment from Earth's 4.54
 * billion years reproduces the site's central claim by brute force: because the
 * four lethal eras occupy 88% of the timeline, roughly nine drops in ten land
 * somewhere you die within a minute. The running tally is the argument — the
 * copy on the index says 88%, this lets the reader watch it happen.
 *
 * Depends on assets/data.js for ERAS, WHY, formatAge and eraFile. Markup it
 * fills is declared in index.html (#roll-*); styling lives in assets/index.css.
 *
 * State is deliberately in-memory only. A tally that survives reload would need
 * storage, consent thinking and a reset affordance for no gain — the interesting
 * number appears within about ten clicks in one sitting.
 */

(function () {
  const btn = document.getElementById('roll-btn');
  if (!btn) return;

  const out = {
    age: document.getElementById('roll-age'),
    era: document.getElementById('roll-era'),
    verdict: document.getElementById('roll-verdict'),
    why: document.getElementById('roll-why'),
    link: document.getElementById('roll-link'),
    panel: document.getElementById('roll-panel'),
    ticks: document.getElementById('roll-ticks'),
    count: document.getElementById('roll-count'),
  };

  const SPAN = ERAS[0].from; // 4,540 Myr
  const results = [];

  /* Uniform over deep time, which is the whole trick: no per-era weighting,
     the eras weight themselves by being different lengths. */
  const sample = () => Math.random() * SPAN;

  const eraAt = (age) => ERAS.find((e) => age <= e.from && age > e.to) || ERAS[ERAS.length - 1];

  function paint(age, settled) {
    const e = eraAt(age);
    out.age.textContent = formatAge(age);
    out.era.textContent = e.name;
    out.verdict.textContent = e.verdict;
    out.panel.className = 'roll__panel band-' + e.band + (settled ? ' is-settled' : '');
    if (!settled) return;
    out.why.textContent = WHY[e.slug];
    out.link.href = eraFile(e);
    out.link.textContent = 'Open ' + e.name + ' →';
    return e;
  }

  function tally(e) {
    results.push(e);
    out.ticks.innerHTML = results
      .map((r) => `<i class="band-${r.band}" title="${r.name}"></i>`)
      .join('');
    const dead = results.filter((r) => r.band === 'minutes').length;
    const lived = results.filter((r) => r.band === 'indefinite').length;
    out.count.textContent =
      `${results.length} drop${results.length === 1 ? '' : 's'} · ` +
      `${dead} dead inside a minute · ${lived} survivable for life`;
  }

  // A single live interval handle. Clicking mid-spin abandons that spin and
  // starts a new one rather than being ignored — the copy tells the reader to
  // roll ten times, so impatient clicking has to be the supported case, and a
  // disabled button would drop exactly those clicks.
  let spin = null;

  const SPIN_MS = 600;

  btn.addEventListener('click', () => {
    clearInterval(spin);
    const started = performance.now();
    // Settle on elapsed wall time, not on a tick count. Browsers clamp timers
    // to ~1s in a backgrounded tab, so counting frames would stretch a 0.6s
    // spin into 11s there and the result would never land.
    spin = setInterval(() => {
      if (performance.now() - started < SPIN_MS) return paint(sample(), false);
      clearInterval(spin);
      spin = null;
      tally(paint(sample(), true));
    }, 55);
  });
})();
