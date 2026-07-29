#!/usr/bin/env python3
"""
gen_img.py — generate era scene images, one or several at a time.

    ./gen_img.py 09            one era
    ./gen_img.py 1 5 9         several
    ./gen_img.py 1-16          a range
    ./gen_img.py all           everything
    ./gen_img.py 09 --dry-run  print the prompt, generate nothing
    ./gen_img.py 09 --flash    cheap model, for throwaway tests

Output goes to assets/scenes/NN-slug.png. Nothing is ever overwritten: a second
run of the same era writes NN-slug-v2.png, then -v3, so alternates can be
compared side by side and the loser deleted by hand.

WHY THE PROMPTS LOOK LIKE THIS
Three models were tried on the same scene. The failure mode that mattered was
not banned objects sneaking in, it was correct-sounding but wrong anatomy:
lycopsid trees rendered as palms or baobabs. Negative prompts do not fix that.
They suppress; they cannot teach. What fixed it was POSITIVE morphology — naming
the organism, then describing trunk geometry, bark pattern and where branching
occurs — which needs a model that comprehends the sentence. Hence
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
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"
PRO = "google/gemini-3-pro-image"
FLASH = "google/gemini-2.5-flash-image"
OUT = pathlib.Path(__file__).resolve().parent / "assets" / "scenes"

# ---------------------------------------------------------------------------
# Shared style contract. Byte-identical in every prompt — this is what makes
# sixteen separate generations read as one series. Muted and desaturated is not
# a taste call: these sit on a near-black page and a saturated image would fight
# the design.
# ---------------------------------------------------------------------------
STYLE = """Photorealistic cinematic landscape, film still shot on 65mm, wide 21:9 \
format. Naturalistic light, volumetric atmospheric haze separating depth layers, \
low sun near the horizon. Desaturated and colour-graded, muted, restrained, \
nothing neon or candy-coloured. Horizon low in the frame, roughly a third from \
the bottom. Distinct foreground, midground and hazy far distance. Empty sky \
across the upper half. Deep, still, uninhabited."""

# Applied to every era on top of its own list. These are failures of the medium
# rather than of the period.
NEVER = ("no text, no letters, no numbers, no watermark, no signature, no border or frame, "
         "no lens flare, no modern objects, no fences, no paths, no buildings")

# ---------------------------------------------------------------------------
# The sixteen. `pal` mirrors that era's block in assets/eras.css so the image
# lands inside the page theme. `scene` carries the morphology. `never` names
# what did not exist yet, which is the part that most needs to be right.
# ---------------------------------------------------------------------------
ERAS = [
    dict(n=1, slug="hadean", pal="#1c0a05 #4a1607 #ff6a24 #ffc247", scene="""
A molten early Earth, 4.2 billion years ago. Black basalt plains fractured by a \
network of glowing orange lava fissures, the crust visibly thin over the melt. \
Low shield volcanoes venting. No liquid water anywhere.

THE MOON DOMINATES THE SKY. It sits only 30,000 km away, roughly thirteen times \
wider than the Moon appears today, filling a large part of the frame. It is dark \
grey-brown, heavily cratered, lit along one edge. Meteor streaks entering the \
atmosphere. The sky is a thick sulfurous red-black, lit from below by the lava.""",
         never="no water, no ocean, no lakes, no plants, no trees, no grass, no animals, "
               "no life of any kind, no blue sky, no white clouds, no snow, no soil"),

    dict(n=2, slug="archean", pal="#241705 #6b3a0c #d8912f #c3cc42", scene="""
A shallow tropical coastal sea, 2.7 billion years ago, under a thick orange \
photochemical methane haze like Titan's atmosphere. The sun is a small dim \
diffused disc, visibly weaker than today.

STROMATOLITES fill the shallow water: low domed and club-shaped mounds built of \
finely laminated mineral layers, like stacked stone cabbages, half-submerged, \
their tops exposed at low tide. The water is a murky green from dissolved iron. \
A low bare black volcanic island on the horizon. The land is naked rock.""",
         never="no plants, no trees, no grass, no moss, no green vegetation on land, "
               "no animals, no fish, no shells, no blue sky, no white clouds"),

    dict(n=3, slug="proterozoic", pal="#071019 #123043 #79b8d6 #d5ecf7", scene="""
Snowball Earth at the Marinoan glaciation, 650 million years ago. A flat white \
sea-ice sheet reaching an unbroken horizon, split by a long lead of black open \
water. Pressure ridges of shattered pale-blue ice thrown up along the fractures. \
Wind-scoured sastrugi on the surface.

The sun sits low and pale with a faint ice-crystal halo around it. The air is \
bitterly dry and clear. Absolutely nothing lives here.""",
         never="no plants, no trees, no grass, no animals, no penguins, no polar bears, "
               "no seals, no birds, no people, no boats, no rock outcrops with vegetation"),

    dict(n=4, slug="ediacaran", pal="#0a1018 #1c2b45 #4a6f8c #4fd3c4", scene="""
A dim shallow sea floor, 560 million years ago, viewed from underwater. Weak \
shafts of light from the surface, suspended particles drifting.

CHARNIA: tall soft frond-shaped organisms standing upright, each anchored to the \
sediment by a round holdfast disc. The frond is built of many small branches \
arranged in a repeating fractal quilted pattern along a central stalk. It has no \
mouth, no eyes, no stem leaves.
DICKINSONIA: flat oval bodies lying directly on the sediment, ribbed into many \
fine parallel quilted segments either side of a midline, like a segmented rubber \
mat.
The sea floor is carpeted in a wrinkled microbial mat, not sand.""",
         never="no fish, no shells, no crabs, no lobsters, no coral, no seaweed, no kelp, "
               "no jellyfish with trailing tentacles, no eyes, no legs, no mouths, no bones"),

    dict(n=5, slug="cambrian", pal="#08141a #15343f #5c9aa3 #3fbfb2", scene="""
A bare rocky coastline 510 million years ago under a pale hazy high-CO2 sky. \
Grey fractured bedrock, loose cobbles and coarse sand meeting a shallow green \
sea.

THE LAND IS COMPLETELY STERILE. Not one plant, not a blade of anything, no soil, \
no lichen, no green tint on the rock. It looks like a Martian shore. Without \
roots to hold sediment the coast is raw stone and shifting gravel.

In the clear shallow water, low segmented armoured arthropods rest on the bottom.""",
         never="no land plants, no grass, no moss, no lichen, no trees, no soil, no green "
               "on land, no fish, no birds, no crabs, no seaweed, no coral reef"),

    dict(n=6, slug="ordovician", pal="#0b141a #223642 #8aa8b6 #d5743f", scene="""
A bare rocky shore 450 million years ago. The only life on land is a thin flat \
crust of liverworts: dark green lobed sheets pressed directly against damp rock \
in the splash zone, no taller than a fingernail, with no stems and no leaves.

In the warm shallow sea behind, a CAMEROCERAS: a giant nautiloid whose shell is \
a long straight narrow cone several metres in length, chambered by visible \
cross-walls, tapering to a point, with a cluster of tentacles at the wide open \
end.

A white glacier front on the far horizon, the Hirnantian ice arriving.""",
         never="no trees, no grass, no upright plants, no leaves, no flowers, no ferns, "
               "no moss cushions, no land animals, no insects, no fish with jaws, no birds"),

    dict(n=7, slug="silurian", pal="#0c1410 #24382a #82a276 #86b84f", scene="""
A low damp coastal plain 425 million years ago, the first land plants in \
existence scattered across wet mud.

COOKSONIA: tiny bright green stems only a few centimetres tall, thinner than a \
pencil. Each stem is completely leafless and forks into two, then forks again, \
and each tip carries a single small round spore capsule like a pinhead. Nothing \
is taller than an ankle. Between them, flat liverwort crusts on the wet ground.

A calm estuary behind under warm, stable, hazy light. The scale is deliberately \
low and intimate: this is a landscape you could step over.""",
         never="no trees, no leaves, no grass, no reeds, no flowers, no ferns, no bushes, "
               "no tall vegetation, no land vertebrates, no birds, no forest"),

    dict(n=8, slug="devonian", pal="#101408 #33401a #b08b3c #74a447", scene="""
The world's first forest, 370 million years ago, on a meandering river bank of \
dark mud.

ARCHAEOPTERIS: the first modern-looking tree. A thick woody trunk with rough \
bark, true lateral branches spaced along its length, and flat fern-like fronds \
of small leaves. Around 25 metres tall, conifer-like in silhouette but \
fern-leaved.
PROTOTAXITES: rising among them, one enormous smooth featureless tapering column \
of pale fungal tissue, twice the height of the trees, with no bark texture, no \
branches and no leaves at all. Just a giant blank organic pillar.

Amber late-afternoon light through the canopy. Fallen logs in the river shallows.""",
         never="no grass, no flowers, no flowering plants, no fruit, no conifers, no pines, "
               "no palms, no broadleaf trees, no dinosaurs, no mammals, no birds, no people"),

    dict(n=9, slug="carboniferous", pal="#08120a #1c3a22 #6aa05a #ff7d2e", scene="""
A dense coal swamp 310 million years ago.

LEPIDODENDRON: the trees are NOT palms and NOT baobabs. Each has a straight, \
unbranched, column-like trunk of near-uniform thickness from base to top, \
covered in a dense diamond-lattice of rhomboid leaf scars like reptile scales. \
No branches anywhere along the trunk. Only at the very top does it split into a \
small tight crown of thin bare repeatedly-forking twigs.
CALAMITES: between them, tall slender hollow bamboo-like stems with clear \
horizontal joints, carrying whorls of fine needle leaves radiating in rings at \
each joint.

The ground is black standing water and bare dark mud strewn with fallen logs. A \
distant orange wildfire and a column of smoke on the horizon.""",
         never="no grass, no grass tufts, no reeds, no palm trees, no palm fronds, no "
               "baobab or bottle-shaped trunks, no flowers, no broadleaf trees, no conifers, "
               "no dinosaurs, no mammals, no birds"),

    dict(n=10, slug="permian", pal="#1a0e07 #4c2411 #c9793a #dfa844", scene="""
The desert interior of the supercontinent Pangaea, 270 million years ago, \
thousands of kilometres from any coast.

Wind-carved rust-orange dune fields and flat-topped eroded mesas of banded red \
sandstone. A wide braided riverbed, bone dry, its channels cracked and \
sun-baked. Airborne dust turns the sun into a hard pale disc with no glare.

GLOSSOPTERIS: sparse low scrub clinging to the dry wash, bearing distinctive \
tongue-shaped leaves with a strong central midrib, growing in loose tufts on \
short woody stems. Nothing else grows.""",
         never="no grass, no flowers, no cactus, no succulents, no palm trees, no conifers, "
               "no dinosaurs, no mammals, no birds, no camels, no people, no oasis"),

    dict(n=11, slug="triassic", pal="#171110 #45302c #b98d7c #a596bb", scene="""
A hot arid basin 240 million years ago on a half-empty planet still recovering \
from the largest extinction in history.

A wide floor of cracked dry mud in polygonal plates, red-bed terraces and \
eroded badlands behind. Visible heat shimmer above the ground. The sky is washed \
out, dusty and pale rather than blue.

Sparse widely spaced ARAUCARIA-like conifers cluster around a shrinking \
waterhole: straight trunks, branches in regular whorls, dense rounded canopies \
of small stiff scale leaves. DICROIDIUM seed ferns in low clumps, their fronds \
forked into a distinctive Y shape. Long distances of bare ground between plants.""",
         never="no grass, no flowers, no broadleaf trees, no palm trees, no cactus, "
               "no mammals, no birds, no large dinosaurs, no people, no green lawn"),

    dict(n=12, slug="jurassic", pal="#081314 #1d3c3c #6fa198 #45a897", scene="""
A humid jade-green forest clearing 155 million years ago. Damp misty light \
shafts through a closed canopy.

ARAUCARIA conifers: very tall, straight, branches in regular whorls, covered in \
stiff overlapping scale-like leaves.
CYCADS: squat barrel-shaped trunks of rough diamond-patterned armour, each \
topped with a stiff rosette of long, hard, palm-like fronds — but they are NOT \
palms and have no smooth ringed trunk.
GINKGO: trees carrying distinctive fan-shaped leaves, split into two lobes.
TREE FERNS and horsetails filling the understory.

There is not a single flower or blade of grass anywhere in this world.""",
         never="no grass, no flowers, no blossom, no flowering plants, no fruit, no palm "
               "trees, no broadleaf deciduous trees, no oak, no maple, no mammals, no birds, "
               "no dinosaurs in frame"),

    dict(n=13, slug="cretaceous", pal="#091223 #1d4a7a #74b3dd #ef8a72", scene="""
A warm floodplain 70 million years ago, a wide slow silt-laden river under a hot \
blue sky with towering cumulus. Ice-free world, deep humid atmospheric distance.

MAGNOLIA: early flowering trees on the near bank, with large simple glossy \
leaves and big pale cup-shaped blooms of thick waxy petals — primitive, \
beetle-pollinated flowers, not delicate modern ones.
FAN PALMS with pleated leaves in the middle distance, and tall conifers on the \
far bank.

Lush and green, but the ground between the trees is bare mud, leaf litter and \
low ferns, not lawn.""",
         never="no grass, no grassland, no lawn, no meadow, no oak, no maple, no modern "
               "orchard fruit, no roses, no daisies, no mammals larger than a cat, no people"),

    dict(n=14, slug="paleogene", pal="#101307 #3b4218 #c4a34a #84b563", scene="""
A dense humid broadleaf forest 45 million years ago, in the hottest stretch of \
the last 66 million years, at a latitude that will one day be temperate.

A closed leafy canopy of large-leaved flowering trees with FAN PALMS growing \
right among them. Thick tangled undergrowth, vines, ferns. Small red and dark \
fruits on shrubs. Steam rising from wet leaf litter in shafts of gold light. \
Standing water and dark rich soil.

Tropical in feel, and nothing about it says cold or seasonal.""",
         never="no grass, no grassland, no open plains, no dinosaurs, no humans, no city, "
               "no conifer forest, no pine trees, no snow, no autumn colours"),

    dict(n=15, slug="neogene", pal="#131207 #4a4018 #c9ab5e #93ac6c", scene="""
Open dry savanna 8 million years ago, at the moment grass took over the world.

Tall golden bunch-grass running unbroken to distant blue hills, moving in the \
wind. Widely spaced flat-topped acacia-like trees with fine compound leaves and \
umbrella crowns, casting long shadows. Dust suspended in low late-afternoon \
light. A vast open sky.

Recognisably the landscape our own lineage evolved in, and completely empty of \
us.""",
         never="no humans, no people, no huts, no fences, no roads, no vehicles, no cattle, "
               "no dinosaurs, no dense forest, no jungle, no mountains with snow"),

    dict(n=16, slug="quaternary", pal="#0a1116 #21384a #9db9cc #e6e2da", scene="""
The mammoth steppe at the Last Glacial Maximum, 20,000 years ago. Cold, dry and \
immense.

Pale wind-scoured tussock grass and low sedge over frozen ground, far more \
productive than modern tundra. Across the entire far horizon, the front of a \
continental ice sheet a kilometre thick, a flat white wall rather than a \
mountain range. A low winter sun in a hard steel-blue sky. Wind-driven snow \
streaming low across the ground.

Bleak, open, and enormous.""",
         never="no trees, no forest, no shrubs taller than a knee, no buildings, no roads, "
               "no vehicles, no modern objects, no snow-capped alpine peaks, no penguins, "
               "no people in frame"),
]

BY_N = {e["n"]: e for e in ERAS}


def build_prompt(era: dict) -> str:
    return (
        f"{STYLE}\n\n"
        f"PALETTE — hold the whole image within these colours and shades between them: {era['pal']}\n"
        f"{era['scene'].strip()}\n\n"
        f"DO NOT INCLUDE ANY OF THE FOLLOWING. They did not exist in this period and their "
        f"presence is a factual error: {era['never']}.\n"
        f"Also: {NEVER}."
    )


def parse_selection(tokens: list[str]) -> list[int]:
    if not tokens or tokens == ["all"]:
        return [e["n"] for e in ERAS]
    out: list[int] = []
    for t in tokens:
        t = t.strip()
        if m := re.fullmatch(r"(\d+)\s*[-.]{1,3}\s*(\d+)", t):
            out += list(range(int(m.group(1)), int(m.group(2)) + 1))
        elif t.isdigit():
            out.append(int(t))
        else:  # allow slugs too
            match = [e["n"] for e in ERAS if e["slug"] == t.lower()]
            if not match:
                sys.exit(f"unknown era: {t!r}")
            out += match
    bad = [n for n in out if n not in BY_N]
    if bad:
        sys.exit(f"era numbers must be 1-16, got: {bad}")
    return list(dict.fromkeys(out))


def next_path(era: dict) -> pathlib.Path:
    """Never overwrite. Second run of an era becomes -v2, then -v3."""
    base = f"{era['n']:02d}-{era['slug']}"
    p = OUT / f"{base}.png"
    if not p.exists():
        return p
    v = 2
    while (OUT / f"{base}-v{v}.png").exists():
        v += 1
    return OUT / f"{base}-v{v}.png"


def generate(era: dict, model: str) -> tuple[pathlib.Path, float]:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": build_prompt(era)}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": "21:9"},
    }
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ekinertac.github.io/deep-time/",
            "X-Title": "Deep Time",
        },
    )
    with urllib.request.urlopen(req, timeout=420) as r:
        data = json.load(r)

    msg = data["choices"][0]["message"]
    images = msg.get("images") or []
    if not images:
        raise RuntimeError(f"no image returned — {json.dumps(msg)[:300]}")
    png = base64.b64decode(images[0]["image_url"]["url"].split(",", 1)[1])
    path = next_path(era)
    path.write_bytes(png)
    return path, float(data.get("usage", {}).get("cost") or 0.0)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Generate Deep Time era scenes.",
        epilog="examples:  ./gen_img.py 09   |   ./gen_img.py 1 5 9   |   ./gen_img.py 1-16   |   ./gen_img.py all",
    )
    ap.add_argument("eras", nargs="*", help="era numbers 1-16, ranges like 1-6, slugs, or 'all'")
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, generate nothing")
    ap.add_argument("--flash", action="store_true", help="use the cheap model (worse anatomy)")
    ap.add_argument("--list", action="store_true", help="list the eras and exit")
    args = ap.parse_args()

    if args.list:
        for e in ERAS:
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
            print(f"\n{'=' * 72}\n{n:02d} {BY_N[n]['slug']}\n{'=' * 72}\n{build_prompt(BY_N[n])}")
        return 0

    if "OPENROUTER_API_KEY" not in os.environ:
        sys.exit("OPENROUTER_API_KEY is not set")

    total = 0.0
    for n in picks:
        era = BY_N[n]
        try:
            path, cost = generate(era, model)
            total += cost
            print(f"  {n:02d} {era['slug']:14s} ${cost:.4f}  {path.stat().st_size // 1024:5d} KB  {path.name}")
        except urllib.error.HTTPError as e:
            print(f"  {n:02d} {era['slug']:14s} HTTP {e.code}: {e.read()[:160].decode()}", file=sys.stderr)
        except Exception as e:  # keep going through a batch
            print(f"  {n:02d} {era['slug']:14s} FAILED: {e}", file=sys.stderr)

    print(f"\n  {len(picks)} requested · ${total:.4f} total · {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
