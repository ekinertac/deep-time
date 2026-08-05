#!/usr/bin/env python3
"""
gen_img.py: generate the image sets for one explorable, one or several at a time.

    tools/gen_img.py 09                   the wide hero scene for item 09
    tools/gen_img.py 09 --set menu        what there is to eat there
    tools/gen_img.py 09 --set kills       the air that kills you there
    tools/gen_img.py 1 5 9 --set menu     several
    tools/gen_img.py 1-16 --set kills     a range
    tools/gen_img.py all --set menu       everything in that set
    tools/gen_img.py 09 --dry-run         print the prompt, generate nothing
    tools/gen_img.py 09 --flash           cheap model, for throwaway tests
    tools/gen_img.py 3 --episode centuries    a different explorable

WHERE THE LINE IS. This file is the engine and knows nothing about any subject:
it does the API call, the seeds, the file naming, the retry-free error handling
and the provenance log. Every word that is specific to one explorable, the item
list, the three prompt sets, the palettes and the captions, lives in that
episode's own prompts.py and is loaded by --episode (default deep-time). Adding
an explorable means writing one prompts.py, not touching this file.

THREE SETS, three jobs, two aspect ratios. `scene` is the 21:9 hero: the place,
wide and distant. `menu` and `kills` are both 3:2 and sit inside the page as
supporting evidence rather than second heroes, one is everything there is to
eat, the other is the air itself. Prompt data and the reasoning behind each set
live in <episode>/prompts.py.

Output goes to <episode>/assets/scenes/<set>/NN-slug.<ext>, one folder per set.
Nothing is ever overwritten: a second run writes NN-slug-v2, then -v3.

KEEP EVERY VARIANT. Do not delete the ones you did not choose. A variant that was
rejected today is the one you want back tomorrow. The chosen image takes the
plain NN-slug name and the rest keep a descriptive suffix
(NN-slug-alt-gas.webp), so the pick is obvious from the filename and nothing is
lost.

REPRODUCIBILITY. Every run now sends an explicit seed and appends a record to
<episode>/assets/scenes/generated.jsonl: the file it wrote, the set, the model, the seed
and the full prompt. A seed on its own is not enough, it only reproduces
against the identical prompt, and these prompts get edited between runs, so both
are stored together. To draw an image again:

    tools/gen_img.py 2 --set menu --seed 704216

Images made before this existed have no seed and cannot be reproduced.

WHY THE PROMPTS LOOK LIKE THIS
Three models were tried on the same scene. The failure mode that mattered was
not banned objects sneaking in, it was correct-sounding but wrong anatomy:
lycopsid trees rendered as palms or baobabs. Negative prompts do not fix that.
They suppress; they cannot teach. What fixed it was POSITIVE morphology: naming
the organism, then describing trunk geometry, bark pattern and where branching
occurs, which needs a model that comprehends the sentence. Hence
google/gemini-3-pro-image rather than a diffusion model, and hence every prompt
below is structured:

    named organism  ->  explicit morphology  ->  DO NOT list

The DO NOT list is still worth having, it is just the second line of defence
rather than the first.

COST: measured, not guessed. About $0.136 per image on gemini-3-pro-image
(1,120 image tokens at $0.00012 per token, plus reasoning). The advertised
"image_output" price is per token, not per image. Actual cost is printed after
every call.

Needs OPENROUTER_API_KEY in the environment.
"""

import argparse
import base64
import datetime as _dt
import importlib
import json
import os
import pathlib
import random
import re
import sys
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"
PRO = "google/gemini-3-pro-image"
FLASH = "google/gemini-2.5-flash-image"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Filled in by load_episode() before anything else runs. Module-level rather
# than threaded through every call because one process only ever works on one
# episode, and passing it everywhere would be ceremony for no benefit.
EP = None          # the episode's prompts module
OUT = None         # <episode>/assets/scenes
LOG = None         # the provenance log inside OUT
ITEMS: list = []   # [{"n": 1, "slug": "hadean"}, ...] in episode order
BY_N: dict = {}


def load_episode(name: str):
    """Import <episode>/prompts.py and point the output paths at that episode.

    An episode owns its items, its three prompt sets and its captions; this file
    owns the API call, the seeds, the file naming and the log. That line is the
    whole reason the series lives in one repo: the parts that were worth getting
    right once are shared, and nothing about Earth's history leaks into the tool.
    """
    global EP, OUT, LOG, ITEMS, BY_N
    d = ROOT / name
    if not (d / "prompts.py").exists():
        sys.exit(f"no episode at {d}/prompts.py")
    sys.path.insert(0, str(d))
    EP = importlib.import_module("prompts")
    OUT = d / "assets" / "scenes"
    LOG = OUT / "generated.jsonl"
    ITEMS = [{"n": i, "slug": slug} for i, slug in enumerate(EP.SLUGS, 1)]
    BY_N = {e["n"]: e for e in ITEMS}

def parse_selection(tokens: list[str]) -> list[int]:
    if not tokens or tokens == ["all"]:
        return [e["n"] for e in ITEMS]
    out: list[int] = []
    for t in tokens:
        t = t.strip()
        if m := re.fullmatch(r"(\d+)\s*[-.]{1,3}\s*(\d+)", t):
            out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif t.isdigit():
            out.append(int(t))
        else:  # allow slugs too
            match = [e["n"] for e in ITEMS if e["slug"] == t.lower()]
            if not match:
                sys.exit(f"unknown item: {t!r}")
            out += match
    bad = [n for n in out if n not in BY_N]
    if bad:
        sys.exit(f"item numbers must be 1-{len(ITEMS)}, got: {bad}")
    return list(dict.fromkeys(out))


def sniff_ext(blob: bytes) -> str:
    """The API returns JPEG or PNG depending on the call, so name the file for
    what it actually is rather than assuming."""
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if blob.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "webp"
    return "bin"


# Set names come from the episode, because the third set is not the same subject
# twice: in deep-time it is the air that kills you, in centuries it is the object
# that decides what you are. Only the shape is fixed, one wide establishing image
# and two detail sets. An episode declares SETS = {name: (folder, ratio)}; the
# fallback keeps deep-time working unchanged if it ever drops the declaration.
DEFAULT_SETS = {"scene": ("hero", "21:9"), "menu": ("menu", "3:2"), "kills": ("kills", "3:2")}


def sets() -> dict:
    return getattr(EP, "SETS", DEFAULT_SETS)


def folder(kind: str) -> str:
    return sets()[kind][0]


def ratio(kind: str) -> str:
    return sets()[kind][1]


def next_path(era: dict, ext: str, kind: str) -> pathlib.Path:
    """Never overwrite. Second run of an era becomes -v2, then -v3, counting
    across every extension so versions stay in one sequence."""
    d = OUT / folder(kind)
    d.mkdir(parents=True, exist_ok=True)
    base = f"{era['n']:02d}-{era['slug']}"
    if not list(d.glob(f"{base}.*")):
        return d / f"{base}.{ext}"
    v = 2
    while list(d.glob(f"{base}-v{v}.*")):
        v += 1
    return d / f"{base}-v{v}.{ext}"


def prompt_for(era: dict, kind: str) -> str:
    return EP.build(kind, era["slug"])


def record(path: pathlib.Path, era: dict, kind: str, model: str, seed: int,
           prompt: str, cost: float) -> None:
    """Append-only provenance. Seed plus prompt, because a seed reproduces
    nothing on its own once the prompt has been edited."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as fh:
        fh.write(json.dumps({
            "at": _dt.datetime.now().isoformat(timespec="seconds"),
            "file": str(path.relative_to(OUT)),
            "set": kind,
            "era": era["slug"],
            "model": model,
            "seed": seed,
            "aspect": ratio(kind),
            "cost": round(cost, 5),
            "prompt": prompt,
        }, ensure_ascii=False) + "\n")


def generate(era: dict, model: str, kind: str, seed: int | None = None) -> tuple[pathlib.Path, float, int]:
    seed = random.randrange(1, 2**31 - 1) if seed is None else seed
    prompt = prompt_for(era, kind)
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": ratio(kind)},
        "seed": seed,
    }
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ekinertac.github.io/explorables/",
            "X-Title": "Explorables",
        },
    )
    with urllib.request.urlopen(req, timeout=420) as r:
        data = json.load(r)

    msg = data["choices"][0]["message"]
    images = msg.get("images") or []
    if not images:
        raise RuntimeError(f"no image returned: {json.dumps(msg)[:300]}")
    blob = base64.b64decode(images[0]["image_url"]["url"].split(",", 1)[1])
    path = next_path(era, sniff_ext(blob), kind)
    path.write_bytes(blob)
    cost = float(data.get("usage", {}).get("cost") or 0.0)
    record(path, era, kind, model, seed, prompt, cost)
    return path, cost, seed


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate the image sets for one explorable.",
        epilog="examples:  tools/gen_img.py 09   |   tools/gen_img.py 1-16 --set menu   |   tools/gen_img.py all --episode centuries",
    )
    ap.add_argument("--episode", default="deep-time",
                    help="which episode directory to generate for (default: deep-time)")
    ap.add_argument("eras", nargs="*", help="item numbers, ranges like 1-6, slugs, or 'all'")
    ap.add_argument("--set", dest="kind", default="scene",
                    help="which image set (default: scene). Names are the episode's own.")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, generate nothing")
    ap.add_argument("--flash", action="store_true", help="use the cheap model (worse anatomy)")
    ap.add_argument("--seed", type=int, default=None,
                    help="reproduce a previous draw (see <episode>/assets/scenes/generated.jsonl)")
    ap.add_argument("--list", action="store_true", help="list the episode's items and exit")
    args = ap.parse_args()
    load_episode(args.episode)
    if args.kind not in sets():
        sys.exit(f"{args.episode} has no set {args.kind!r}. It has: {', '.join(sets())}")

    if args.list:
        for e in ITEMS:
            print(f"  {e['n']:02d}  {e['slug']}")
        return 0
    if not args.eras:
        ap.print_help()
        return 1

    model = FLASH if args.flash else PRO
    OUT.mkdir(parents=True, exist_ok=True)
    picks = parse_selection(args.eras)

    if args.dry_run:
        for n in picks:
            era = BY_N[n]
            print(f"\n{'=' * 72}\n{args.kind}  {n:02d} {era['slug']}  ({ratio(args.kind)})\n{'=' * 72}")
            print(prompt_for(era, args.kind))
            if args.kind != "scene":
                print(f"\n[page caption] {EP.caption(args.kind, era['slug'])}")
        return 0

    if "OPENROUTER_API_KEY" not in os.environ:
        sys.exit("OPENROUTER_API_KEY is not set")

    total = 0.0
    for n in picks:
        era = BY_N[n]
        try:
            path, cost, seed = generate(era, model, args.kind, args.seed)
            total += cost
            print(f"  {n:02d} {era['slug']:14s} ${cost:.4f}  {path.stat().st_size // 1024:5d} KB  "
                  f"seed {seed:<11d} {path.name}")
        except urllib.error.HTTPError as e:
            print(f"  {n:02d} {era['slug']:14s} HTTP {e.code}: {e.read()[:160].decode()}", file=sys.stderr)
        except Exception as e:  # keep going through a batch
            print(f"  {n:02d} {era['slug']:14s} FAILED: {e}", file=sys.stderr)

    print(f"\n  {args.kind}: {len(picks)} requested · ${total:.4f} total · {OUT / folder(args.kind)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
