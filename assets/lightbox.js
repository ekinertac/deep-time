/*
 * lightbox.js — click any scene image to view it large.
 *
 * The three images on an era page are displayed at roughly a third of their
 * native size, and they carry detail worth looking at: the diamond leaf-scar
 * lattice on Lepidodendron bark, the ribbing on a Dickinsonia, individual spores
 * hanging in Devonian air. This opens them at full size.
 *
 * Built on the native <dialog> element rather than a hand-rolled overlay, which
 * hands us the focus trap, the inert background, the backdrop and Esc-to-close
 * for free — all of which are easy to get wrong by hand.
 *
 * Two zoom levels. Default fits the viewport, which is already a 2–3x jump from
 * the inline size on a desktop. Clicking the image switches to actual pixels and
 * lets the stage scroll, which is the only way to see detail on a phone where
 * "fit the viewport" is not a zoom at all.
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
      <span class="lb__hint">&larr; &rarr; between images &middot; click to zoom &middot; Esc to close</span>
    </div>`;
  document.body.append(dlg);

  const stage = dlg.querySelector('.lb__stage');
  const big = dlg.querySelector('.lb__img');
  const count = dlg.querySelector('.lb__count');
  const cap = dlg.querySelector('.lb__cap');
  let i = 0;

  function show(n) {
    i = (n + imgs.length) % imgs.length;
    const src = imgs[i];
    stage.classList.remove('is-zoomed');
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

  // Clicking the picture toggles between fit-to-viewport and actual pixels.
  big.addEventListener('click', (e) => {
    e.stopPropagation();
    stage.classList.toggle('is-zoomed');
    if (stage.classList.contains('is-zoomed')) {
      // Centre the view on the click, so zooming goes where you pointed.
      const r = big.getBoundingClientRect();
      stage.scrollLeft = (e.clientX - r.left) / r.width * stage.scrollWidth - stage.clientWidth / 2;
      stage.scrollTop = (e.clientY - r.top) / r.height * stage.scrollHeight - stage.clientHeight / 2;
    }
  });

  dlg.querySelector('.lb__close').addEventListener('click', () => dlg.close());
  // Anywhere outside the picture closes. The stage fills the dialog, so this is
  // the backdrop-click behaviour people expect.
  dlg.addEventListener('click', (e) => { if (e.target !== big) dlg.close(); });

  dlg.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(i - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(i + 1); }
  });

  // Free the memory and stop a stale frame flashing on the next open.
  dlg.addEventListener('close', () => { big.removeAttribute('src'); });
})();
