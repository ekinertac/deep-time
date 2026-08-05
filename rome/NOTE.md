# Property, Pilgrim, Papers

**Concept in one line:** one continuous descent through twenty centuries of the same
city, with a WebGL model of Rome behind the text whose block count tracks the real
population, so you watch a million people drain out of the walls and the traveller's
survival go *up*.

## Structure

Gate → the terms of the drop → twenty century panels with eight interrupts cut into
them (three dated statements, five image plates) → the payoff chart → the three
regimes → the plague/labour paradox → the closing line → what is soft, and sources.

The instruments are the fixed readout bottom left (century, years, inhabitants,
schematic street level, verdict) and the tick rail on the right, which is navigation
and the survival chart at the same time: tick length is log months alive and free.

The model is a diagram, not a map, and the page says so twice. One block is about 300
people at the same exchange rate in every century, which is where the drama comes from:
~3,000 blocks in the 2nd century, 55 in the 14th, spilling outside the wall in the 20th.
Blocks are scattered across the whole walled area in late antiquity and contract into
the Tiber bend from the 11th century, following Dey's revision of Krautheimer rather than
the old "6th-century huddle" story. The wall does not exist until 271 and rises when you
reach the 3rd century. Eight monuments never disappear, because they did not.

## Fonts and libraries

All self-hosted under `assets/fonts/`, all OFL: **Cinzel** (Trajan-derived capitals, used
only for century numerals and small labels), **Instrument Serif** (display), **Spectral**
(body), **Space Mono** (all data and captions). Deliberately shares nothing with episode
01, which is Big Shoulders / Newsreader / IBM Plex Mono. One library: **three.js r169**
(MIT), vendored at `assets/vendor/three.module.min.js`, 687 KB. No CDN, no API key, no
third-party request of any kind.

## Images to generate

Placeholders are in place with the shape and register I want. All five plates are 21:9
full-bleed. Register: dim, warm, low raking light, archaeological rather than cinematic;
no faces in close-up, no legible text in the image, no modern colour grading.

1. `assets/img/01-wall.webp` — the Aurelian Wall under construction, 271 CE. Brick-faced
   concrete, scaffolding, a nineteen-kilometre line being drawn around a city that thought
   it would never need one.
2. `assets/img/02-dry-arches.webp` — a dry aqueduct arcade crossing empty country outside
   the walls, 6th century. Dust, broken channel, sheep, no water.
3. `assets/img/03-schola.webp` — the Schola Saxonum in the Borgo, 8th century: a low walled
   compound of lodging, kitchen and church, arrivals sleeping in the courtyard.
4. `assets/img/04-campo-vaccino.webp` — the Forum as pasture: cattle among half-buried
   column drums and the tops of arches, ground level metres above the ancient pavement.
5. `assets/img/05-register.webp` — a parish register open on a table, quill, candle, ruled
   columns of names: the *stato delle anime*.
6. `assets/img/og-card.jpg` — 1200×630 social card, referenced in the head, not yet made.

Swapping a placeholder for the real thing means putting the file at the path in
`BEATS[].src` in `assets/data.js` and rendering an `<img>` instead of the box in
`beatHTML()` in `assets/page.js`. That is the only wiring left.

## Serving it

`scene.js` is an ES module, so `file://` will not load it (the module import is blocked
by CORS and you get the page with no city). Serve the folder over http:
`python3 -m http.server 8788` from the directory, then `http://127.0.0.1:8788/`. One is
already running on that port from this session.

## Verified, and not

Checked in Chrome at 1440×900: hero, several century panels, the 537 beat, an image
plate, the payoff chart, the regimes, the closing line, the sources. 121 fps sitting on
the descent with ~9,000 instanced blocks and a 2048 shadow map. No console errors. Total
page height is 34,000 px, which is a lot, and deliberate.

Not verified: true 390 px, because Chrome will not size a window below 500 px wide — I
tested at 500 px and simulated 390 with a root zoom, and the narrow layout (full-width
cards, readout as a bottom bar, gutter for the rail) holds at both.
`prefers-reduced-motion` and the no-WebGL path are correct by construction (the reveal
animations and the camera smoothing are switched off by the media query and by
`RomeState.reduced`; scene.js is a module that throws on context creation and takes
nothing with it, since all reading content is plain DOM built by `page.js`) but I could
not emulate either through the browser tooling, so neither has been seen with my own eyes.

Every figure is sourced and every contested one carries its range and its dispute in the
copy, not in a footnote. The survival durations are the one editorial thing on the page:
they are reasoned scenarios, the clock is defined as "dead **or** owned", and the closing
section says plainly that nobody has run the experiment.
