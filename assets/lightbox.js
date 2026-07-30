/*
 * lightbox.js: click any scene image to view it large.
 *
 * The three images on an era page are displayed at roughly a third of their
 * native size, and they carry detail worth looking at: the diamond leaf-scar
 * lattice on Lepidodendron bark, the ribbing on a Dickinsonia, individual spores
 * hanging in Devonian air. This opens them at full size.
 *
 * Built on the native <dialog> element rather than a hand-rolled overlay, which
 * hands us the focus trap, the inert background, the backdrop and Esc-to-close
 * for free, all of which are easy to get wrong by hand.
 *
 * The image is shown fit-to-viewport, which is a 2–3x jump from the inline size.
 * Clicking anywhere closes, the picture included: an actual-pixel zoom toggle
 * lived here briefly and fought the obvious expectation that clicking a lightbox
 * dismisses it.
 *
 * Progressive enhancement: with JS off the images are still images. The triggers
 * are given role and tabindex here rather than in the markup so that a
 * non-interactive image is never announced as a button.
 *
 * Depends on nothing. Styling lives in assets/site.css (.lb*). Loaded by the
 * sixteen era pages; nav.js is told to ignore arrow keys while it is open, since
 * both want them.
 */

(function () {
  const imgs = [...document.querySelectorAll('.scene img, .split__fig img')];
  if (!imgs.length || typeof HTMLDialogElement === 'undefined') return;

  const capFor = (img) => {
    const cap = img.closest('figure')?.querySelector('figcaption');
    return cap ? cap.textContent.trim() : '';
  };

  const dlg = document.createElement('dialog');
  dlg.className = 'lb';
  dlg.innerHTML = `
    <button class="lb__close" type="button" aria-label="Close">&times;</button>
    <div class="lb__stage"><img class="lb__img" alt=""></div>
    <div class="lb__bar">
      <span class="lb__count"></span>
      <span class="lb__cap"></span>
      <span class="lb__hint">&larr; &rarr; between images &middot; click anywhere to close</span>
    </div>`;
  document.body.append(dlg);

  const big = dlg.querySelector('.lb__img');
  const count = dlg.querySelector('.lb__count');
  const cap = dlg.querySelector('.lb__cap');
  let i = 0;

  function show(n) {
    i = (n + imgs.length) % imgs.length;
    const src = imgs[i];
    big.src = src.currentSrc || src.src;
    // The thumbnail's alt already describes the picture; reusing it keeps one
    // description rather than letting a second one drift out of date.
    big.alt = src.alt;
    cap.textContent = capFor(src);
    count.textContent = `${i + 1} / ${imgs.length}`;
  }

  function open(n) {
    show(n);
    dlg.showModal();
  }

  imgs.forEach((img, n) => {
    img.classList.add('is-zoomable');
    img.tabIndex = 0;
    img.setAttribute('role', 'button');
    img.setAttribute('aria-label', `View larger: ${img.alt}`);
    img.addEventListener('click', () => open(n));
    img.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(n); }
    });
  });

  dlg.querySelector('.lb__close').addEventListener('click', () => dlg.close());
  // Any click closes, including on the picture itself. An earlier version made
  // clicking the image toggle an actual-pixel zoom, which fought the obvious
  // expectation that clicking a lightbox dismisses it.
  dlg.addEventListener('click', () => dlg.close());

  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); }
  });

  // Free the memory and stop a stale frame flashing on the next open.
  dlg.addEventListener('close', () => { big.removeAttribute('src'); });
})();
