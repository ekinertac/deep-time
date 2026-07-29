/*
 * data.js — the single source of truth for the 16 era entries.
 *
 * Role in the system: every page in this site is static HTML, but the *navigation*
 * (prev/next links, the deep-time rail, the index timeline) is generated from this
 * array so the order and labels can never drift between 17 hand-written files.
 * Loaded by index.html and by every page under eras/, then consumed by nav.js.
 *
 * Each entry:
 *   slug     file basename under eras/ (without .html)
 *   n        1-based ordinal, matches the NN- filename prefix
 *   name     display name
 *   from/to  start and end in millions of years ago (to: 0 = present)
 *   verdict  the survival headline, kept short enough for the rail tooltip
 *   band     survival regime, drives the colour coding on the index:
 *            'minutes' | 'weeks' | 'months' | 'years' | 'indefinite'
 *
 * Related files: assets/nav.js (renders from this), assets/eras.css (theme per slug),
 * index.html (timeline). Duration is derived (from - to), never stored, so the
 * proportional timeline can't disagree with the dates printed on the era page.
 */

const ERAS = [
  { slug: 'hadean',        n: 1,  name: 'Hadean',        from: 4540,   to: 4031,  verdict: '~1 minute',   band: 'minutes' },
  { slug: 'archean',       n: 2,  name: 'Archean',       from: 4031,   to: 2500,  verdict: '~2 minutes',  band: 'minutes' },
  { slug: 'proterozoic',   n: 3,  name: 'Proterozoic',   from: 2500,   to: 635,   verdict: '~3 minutes',  band: 'minutes' },
  { slug: 'ediacaran',     n: 4,  name: 'Ediacaran',     from: 635,    to: 538.8, verdict: '~15 minutes', band: 'minutes' },
  { slug: 'cambrian',      n: 5,  name: 'Cambrian',      from: 538.8,  to: 486.9, verdict: '~3 weeks',    band: 'weeks' },
  { slug: 'ordovician',    n: 6,  name: 'Ordovician',    from: 486.9,  to: 443.8, verdict: '~4 weeks',    band: 'weeks' },
  { slug: 'silurian',      n: 7,  name: 'Silurian',      from: 443.8,  to: 419.2, verdict: '~2 months',   band: 'months' },
  { slug: 'devonian',      n: 8,  name: 'Devonian',      from: 419.2,  to: 358.9, verdict: 'a year plus', band: 'years' },
  { slug: 'carboniferous', n: 9,  name: 'Carboniferous', from: 358.9,  to: 298.9, verdict: 'years',       band: 'years' },
  { slug: 'permian',       n: 10, name: 'Permian',       from: 298.9,  to: 251.9, verdict: '~4 months',   band: 'months' },
  { slug: 'triassic',      n: 11, name: 'Triassic',      from: 251.9,  to: 201.4, verdict: '~6 weeks',    band: 'weeks' },
  { slug: 'jurassic',      n: 12, name: 'Jurassic',      from: 201.4,  to: 145,   verdict: '~2 months',   band: 'months' },
  { slug: 'cretaceous',    n: 13, name: 'Cretaceous',    from: 145,    to: 66,    verdict: 'a year plus', band: 'years' },
  { slug: 'paleogene',     n: 14, name: 'Paleogene',     from: 66,     to: 23,    verdict: 'indefinite',  band: 'indefinite' },
  { slug: 'neogene',       n: 15, name: 'Neogene',       from: 23,     to: 2.58,  verdict: 'indefinite',  band: 'indefinite' },
  { slug: 'quaternary',    n: 16, name: 'Quaternary',    from: 2.58,   to: 0,     verdict: 'indefinite',  band: 'indefinite' },
];
