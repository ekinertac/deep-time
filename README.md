# Deep Time

Sixteen eras of Earth's history, each rated by how long an unequipped modern
human would last in it. You arrive with the clothes you are wearing and a knife.

The short version: oxygen is the filter for the first four billion years, food is
the filter for the next hundred million, and only the last 1.5% of Earth's
history would let you live out a normal life.

## What's here

- `index.html` sizes every era by its true share of 4.54 Gyr, so the four eras
  that kill you inside a minute physically occupy 88% of the page. It also has a
  randomiser that samples a uniform moment from deep time, which reproduces that
  88% by brute force in about twenty clicks.
- `eras/01..16-*.html`, one page per era: a verdict, a generated scene image
  (prompts and regeneration live in `gen_img.py`, files in `assets/scenes/hero,menu,kills/`), six
  vital statistics with meters against today's values, a cause-of-death timeline
  scaled to that era, a survival kit, and a section on what the science actually
  disagrees about.
- `chart.html` puts oxygen, CO2 and mean temperature on one shared time axis.
  Three panels, never a dual axis. The axis breaks at 539 Ma because a linear
  scale squeezes the entire Phanerozoic into the last 12% of the width.

## Running it

Static files. No build step, no dependencies, no framework.

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000`. Opening `index.html` over `file://` also works
apart from the fonts.

## About the numbers

Era boundaries follow the ICS 2023 chart. The per-era figures come from published
reconstructions and each page ends with a section naming what is contested rather
than stating everything flat. That matters more than usual here: atmospheric
oxygen before the Devonian is model output, and independent groups disagree by
roughly a factor of two on the Cambrian and Carboniferous values.

The three curves on `chart.html` are a synthesis resampled onto a common grid so
quantities on very different scales can share an axis. They are not a published
dataset. The shapes, the crossings and the order of events are the claim. The
individual values are not precise and should not be quoted as measurements.

## Colours

The chart's series colours were validated rather than chosen: worst colour-vision
separation dE 9.4 and worst normal-vision separation dE 20.9 under an all-pairs
check, on the dark surface the site actually uses.

The five survival-band colours on the index have a known defect. Weeks-orange and
months-amber sit at dE 11.5, under the 15 floor, so they are harder to tell apart
than they should be, and a five-hue rainbow is the wrong encoding for ordered
data anyway. Not yet fixed.

## Licence

MIT.
