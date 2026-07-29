/*
 * nav.js — generates every cross-page link in the site.
 *
 * Why this exists: with 17 hand-written HTML files, hard-coding a 16-item rail
 * and a prev/next pager into each one guarantees they drift apart. Instead each
 * page ships an empty <nav class="rail"> / <nav class="pager"> and this script
 * fills them from the ERAS array in data.js.
 *
 * Depends on: assets/data.js (must load first — plain script, no modules).
 * Styles for the markup it emits live in assets/site.css (.rail, .pager).
 *
 * Path handling: era pages sit in eras/ and the index sits at the root, so link
 * prefixes differ. `data-era="index"` on <body> is the discriminator; every
 * other value is treated as an era slug and resolves siblings with './'.
 *
 * Also binds ArrowLeft / ArrowRight to the pager, which is the main reason the
 * site is pleasant to read straight through.
 */

(function () {
  const slug = document.body.dataset.era;
  const onIndex = slug === 'index';
  // Files are named NN-slug.html so they sort correctly in a directory listing;
  // the slug alone is the identity used everywhere else.
  const eraHref = (e) => (onIndex ? 'eras/' : './') + String(e.n).padStart(2, '0') + '-' + e.slug + '.html';
  const homeHref = onIndex ? '#top' : '../index.html';
  const here = ERAS.findIndex((e) => e.slug === slug);

  /* ---- left rail: all 16, current one highlighted ---- */
  const rail = document.querySelector('.rail');
  if (rail) {
    rail.innerHTML =
      `<a class="rail__home" href="${homeHref}">all</a><div class="rail__list">` +
      ERAS.map(
        (e) =>
          `<a class="rail__item" href="${eraHref(e)}"${
            e.slug === slug ? ' aria-current="page"' : ''
          } title="${e.name} — ${e.verdict}">${String(e.n).padStart(2, '0')}<span>${e.name}</span></a>`
      ).join('') +
      `</div>`;
  }

  /* ---- pager: only on era pages ---- */
  const pager = document.querySelector('.pager');
  if (pager && here !== -1) {
    const prev = ERAS[here - 1];
    const next = ERAS[here + 1];
    const cell = (e, dir) =>
      e
        ? `<a class="pager__link pager__link--${dir}" href="${eraHref(e)}" rel="${dir}">
             <div class="pager__dir">${dir === 'prev' ? '← Older' : 'Younger →'}</div>
             <div class="pager__name">${e.name}</div>
             <div class="pager__verdict">${e.verdict}</div>
           </a>`
        : `<div class="pager__link pager__empty"></div>`;
    pager.innerHTML = cell(prev, 'prev') + cell(next, 'next');

    // Keyboard paging. Ignored while the user is typing or holding a modifier,
    // so it never fights browser shortcuts or a future search box.
    document.addEventListener('keydown', (ev) => {
      if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) return;
      if (ev.key === 'ArrowLeft' && prev) location.href = eraHref(prev);
      if (ev.key === 'ArrowRight' && next) location.href = eraHref(next);
    });
  }
})();
