# Explorables

Self-contained sites that take a fixed set of things, ask one question with a
number for an answer, and follow that number until it says something the set
alone would not.

Live at <https://ekinertac.github.io/explorables/>.

| # | Episode | The set | The question |
|---|---------|---------|--------------|
| 01 | [Deep Time](deep-time/) | 16 intervals of Earth's history | How long would an unequipped modern human survive in each? |

## What makes one of these

The format is narrow on purpose. A candidate that misses any of these is a
listicle with better typography.

1. **A fixed, ordered set that already exists.** Sixteen geological intervals,
 not sixteen things chosen to make a point. Nothing to argue with before the
 argument starts.
2. **One scalar answer per item, spanning orders of magnitude.** Two minutes to
 decades. The range is what makes the comparison worth drawing.
3. **A hidden variable that switches partway through.** In Deep Time the filter
 is oxygen for four billion years and then food. Without a switch there is no
 finding, only a table.
4. **One page per item on a single schema**, so pages are comparable instead of
 each being a fresh essay.
5. **A section naming what is contested.** Every episode ends each page with
 where its numbers are soft. That section is the credibility, not a disclaimer.
6. **Three image sets, each with a job.** The place, what there is to eat, and
 the thing that kills you.

## Layout

```
assets/        shared by every episode: site.css, fonts, lightbox.js, favicon
tools/         gen_img.py, the image engine, knows nothing about any subject
<episode>/     one directory per explorable, self-contained
  index.html   that episode's front page
  prompts.py   its items, prompt sets, palettes and captions
  assets/      its own data.js, themes and generated images
index.html     the shelf
```

The split between `tools/gen_img.py` and `<episode>/prompts.py` is the one that
matters. The engine owns the API call, the seeds, the file naming and the
provenance log. The episode owns every word specific to its subject. Adding an
explorable means writing a `prompts.py`, not editing the tool.

```sh
tools/gen_img.py 1-16 --set kills                # deep-time by default
tools/gen_img.py all --set menu --episode centuries
```

## Running it

Static files. No build step, no dependencies, no framework.

```sh
python3 -m http.server 8000
```

## Licence

MIT.
