"""
scene_prompts.py — the prompt data for all three image sets. No logic here.

Split out of gen_img.py because this is data and that is a CLI, and because
three sets of sixteen made one file too long to hold in your head.

THE THREE SETS, and why each looks the way it does:

  scene  21:9, full width, opens each era page. The place: wide, calm, distant,
         empty. Carries the era's own palette from assets/eras.css.

  menu   3:2, sits in "If you survive". Everything there is to eat, lying on
         that era's own ground. Deliberately the opposite register: close,
         static, overhead, forensic. NEUTRAL daylight rather than the era
         palette — tinting rock orange to match a theme would misrepresent what
         you would actually see, and a specimen plate should look like evidence.
         The first four eras have nothing edible at all; those frames carry an
         inedible subject instead (a bacterial smear, a soft frond) so the
         emptiness has something to be measured against. The page caption names
         the contents, which is what makes an empty plate legible.

  kills  3:2, sits in "What kills you". THE AIR IS THE SUBJECT. Six of the
         sixteen are killed by something with no appearance — gas, hypoxia,
         a missing vitamin — so rather than solving that era by era, every
         frame in this set shows the medium you have to survive inside and
         whatever it is carrying: vapour, haze, frost, spores, embers, dust,
         ejecta, snow. For the anoxic eras the air genuinely is the murderer,
         which is also the site's central claim. These DO take the era palette,
         because here the colour of the air is the information.

Prompt structure is the same in all three sets and was arrived at empirically:
named subject -> explicit morphology -> DO NOT list. Positive morphology is what
fixes anatomy; the DO NOT list is the second line of defence, not the first.
See the header of gen_img.py for the model bake-off that established this.
"""

# ---------------------------------------------------------------------------
# Shared style contracts. Byte-identical within a set — this is what makes
# sixteen separate generations read as one series.
# ---------------------------------------------------------------------------

SCENE_STYLE = """Photorealistic cinematic landscape, film still shot on 65mm, wide 21:9 \
format. Naturalistic light, volumetric atmospheric haze separating depth layers, \
low sun near the horizon. Desaturated and colour-graded, muted, restrained, \
nothing neon or candy-coloured. Horizon low in the frame, roughly a third from \
the bottom. Distinct foreground, midground and hazy far distance. Empty sky \
across the upper half. Deep, still, uninhabited."""

MENU_STYLE = """Photorealistic overhead still-life, 3:2 format, shot on 65mm macro \
with soft directional daylight. A natural-history specimen arrangement \
photographed in situ: the items lie directly on the era's own ground. Shallow \
depth of field, sharp on the subject and falling off at the edges. Neutral \
daylight colour, desaturated and muted. Cold, forensic and completely still.

ABSOLUTELY NO man-made objects: no plate, no bowl, no dish, no board, no basket, \
no cloth, no cutlery, no jar, no rope, no tools, no knife. No hands, no people."""

KILLS_STYLE = """Photorealistic close detail, 3:2 format, shot on 65mm at ground \
level. THE AIR ITSELF IS THE SUBJECT OF THIS PICTURE — what the atmosphere is \
made of and what it is carrying. Volumetric light raking through the medium so \
that vapour, particles and motion are visible. Close, dense, oppressive and \
claustrophobic, the opposite of a wide open vista. Shallow depth, the far \
distance swallowed. Desaturated and colour-graded, muted.

No human figures, no hands, no bodies, no skulls, no skeletons, no corpses."""

# Failures of the medium rather than of the period. Appended to every prompt.
NEVER = ("no text, no letters, no numbers, no watermark, no signature, no border or frame, "
         "no lens flare, no modern objects, no fences, no paths, no buildings")

# Order and slugs must match ERAS in assets/data.js.
SLUGS = [
    "hadean", "archean", "proterozoic", "ediacaran", "cambrian", "ordovician",
    "silurian", "devonian", "carboniferous", "permian", "triassic", "jurassic",
    "cretaceous", "paleogene", "neogene", "quaternary",
]

# Mirrors each era's block in assets/eras.css.
PALETTES = {
    "hadean": "#1c0a05 #4a1607 #ff6a24 #ffc247",
    "archean": "#241705 #6b3a0c #d8912f #c3cc42",
    "proterozoic": "#071019 #123043 #79b8d6 #d5ecf7",
    "ediacaran": "#0a1018 #1c2b45 #4a6f8c #4fd3c4",
    "cambrian": "#08141a #15343f #5c9aa3 #3fbfb2",
    "ordovician": "#0b141a #223642 #8aa8b6 #d5743f",
    "silurian": "#0c1410 #24382a #82a276 #86b84f",
    "devonian": "#101408 #33401a #b08b3c #74a447",
    "carboniferous": "#08120a #1c3a22 #6aa05a #ff7d2e",
    "permian": "#1a0e07 #4c2411 #c9793a #dfa844",
    "triassic": "#171110 #45302c #b98d7c #a596bb",
    "jurassic": "#081314 #1d3c3c #6fa198 #45a897",
    "cretaceous": "#091223 #1d4a7a #74b3dd #ef8a72",
    "paleogene": "#101307 #3b4218 #c4a34a #84b563",
    "neogene": "#131207 #4a4018 #c9ab5e #93ac6c",
    "quaternary": "#0a1116 #21384a #9db9cc #e6e2da",
}


# ---------------------------------------------------------------------------
# MENU — everything there is to eat, and the page caption that names it.
# `cap` is rendered as HTML under the figure, never drawn into the image.
# ---------------------------------------------------------------------------
MENU = {
"hadean": dict(
    cap="Nothing. Bare basalt and a little condensed water.",
    scene="""
THERE IS NOTHING TO EAT AND THE EMPTINESS IS THE SUBJECT OF THE PICTURE. Only \
bare black basalt, freshly cooled, glassy and cracked, with a shallow depression \
holding a little cloudy condensed water. Faint yellow sulfur staining at the rock \
edges. Not one organic object anywhere in frame.""",
    never="no plants, no leaves, no seeds, no shells, no bones, no meat, no fish, no eggs, "
          "no fruit, no moss, no algae, no insects, no wood, no food of any kind"),

"archean": dict(
    cap="Bacterial mat, peeled off a stromatolite. Technically organic. Not food.",
    scene="""
THE SUBJECT IS A FLAT WIDE SHEET OF SLIMY BACTERIAL MAT, filling the whole frame \
edge to edge like a skin stretched over shallow water. Blackish-green shading to \
olive and rust, glistening wet, the surface finely wrinkled and creased all over \
like the skin on cooling milk. It lies FLAT. There is no single lump, no central \
mass, no lifted or folded-over flap, and nothing in it should resemble an animal \
or a body.

THE GAS IS THE DETAIL THAT MATTERS. The mat is being inflated from below by gas \
the bacteria are producing. Across the sheet: some bubbles still trapped and \
domed, stretching the film taut and shiny; others already burst, leaving ragged \
open craters with the torn film curled back around the rim; and at two or three \
of them, gas actively escaping — a fine stream of small bubbles breaking the \
water surface, with faint ripples spreading out from the vent.

Ragged torn edges to the sheet. It should look organic, dense, faintly repellent \
and completely inedible.""",
    never="no plants, no leaves, no seaweed, no kelp, no shells, no fish, no meat, no bones, "
          "no seeds, no fruit, no insects, no wood, no fungi, no mushrooms, no lichen, "
          "no bare dry rock filling the frame"),

"proterozoic": dict(
    cap="Ice, meltwater and stone. The plate stays empty for another 1.9 billion years.",
    scene="""
THERE IS NOTHING TO EAT. A slab of blue-white glacial ice resting on dark wet \
stone, its surface pocked and melting, a thin film of meltwater running off into \
a shallow pool. Frost crystals along the shaded edges. Utterly sterile: no \
colour, no organic matter, nothing living or dead.""",
    never="no plants, no algae, no moss, no lichen, no fish, no shells, no meat, no bones, "
          "no seeds, no seaweed, no penguins, no food of any kind"),

"ediacaran": dict(
    cap="Two Dickinsonia. Soft, boneless, and of entirely unknown food value.",
    scene="""
THE FIRST LARGE ORGANISMS, AND NOBODY KNOWS IF THEY ARE EDIBLE. Two DICKINSONIA \
bodies of different sizes lying flat on wet grey-green sediment, one about twice \
the length of the other.

CRITICAL SHAPE — GET THIS RIGHT: each body is a LONG NARROW OVAL, two to three \
times longer than it is wide, rounded at both ends with one end slightly \
narrower, like the outline of a shoe sole or a flattened leech. Running the FULL \
LENGTH of the body, from one end to the other, is a single straight central \
groove. Off that long groove, many dozens of fine soft ribs run sideways to the \
outer margin, and because the groove is a long line rather than a point, these \
ribs sit NEARLY PARALLEL to one another along the whole middle section of the \
body, like the rungs of a ladder or the segments of a woodlouse. The ribs on one \
side are offset half a step against those on the other.

IT IS NOT A FAN AND NOT A SHELL. The ribs must NOT radiate outward from one \
central point. There is no hinge, no valve, no hard rim, no scallop or cockle \
outline, and nothing rigid anywhere.

Both bodies are limp, soft, boneless, thinner than a coin, wet, and translucent \
at the edges where they meet the sediment. The sediment around them is a \
wrinkled elephant-skin microbial mat with faint drag traces.""",
    never="no shells, no scallops, no cockles, no clams, no oysters, no hinges, no valves, "
          "no fan shape, no ribs radiating from a central point, no ferns, no fern fronds, "
          "no leaves, no leaf veins, no plants, no seaweed, no fish, no crabs, no prawns, "
          "no bones, no eyes, no legs, no mouths, no jellyfish"),

"cambrian": dict(
    cap="Trilobites and brachiopods. Raw, because there is nothing on Earth to burn.",
    scene="""
THE ENTIRE FOOD SUPPLY OF THIS ERA: raw marine arthropods and shellfish gathered \
from the tideline, lying on wet grey fractured bedrock.

Three or four TRILOBITES: flat oval armoured bodies, each with a raised central \
axial lobe running head to tail, flanked either side by many fine ribbed \
segments, a smooth crescent-shaped head shield at the front, and small jointed \
legs beneath the rim. Dull grey-brown chitin, wet.

Beside them a scatter of small smooth double-valved brachiopod shells. Everything \
is raw, cold and dripping. There is no fire and no way to cook any of it, and no \
plant matter of any kind is present because none exists on land yet.""",
    never="no fire, no cooked or grilled food, no plants, no herbs, no leaves, no vegetables, "
          "no lemon, no bread, no crab, no lobster, no shrimp, no prawns, no modern fish, "
          "no seaweed"),

"ordovician": dict(
    cap="Nautiloid, opened. The first meal on this list with real fat in it.",
    scene="""
THE FIRST FAT IN EARTH'S HISTORY. On wet dark rock: a section of the long \
straight conical shell of a CAMEROCERAS nautiloid, cracked open lengthwise to \
show the chambered interior divided by curved cross-walls, with a mass of pale \
soft cephalopod flesh and short thick tentacles spilling from the wide end. The \
flesh is dense and marbled, unlike anything else available.

Beside it, several small ribbed shellfish and a thin flat crust of dark green \
liverwort peeled off a rock — the only plant matter that exists, and inedible.""",
    never="no squid rings, no calamari, no cooked food, no fire, no herbs, no vegetables, "
          "no lemon, no trees, no leaves, no grass, no seeds, no fruit, no modern seafood platter"),

"silurian": dict(
    cap="Arthropods to eat, and dried stems to burn. The fuel matters more than the food.",
    scene="""
THE TURNING POINT: FOR THE FIRST TIME THERE IS SOMETHING TO BURN. On damp mud, \
two small bundles side by side.

FOOD: several small dark segmented millipede-like arthropods and a few shellfish, \
raw and unappetising.
FUEL: a loose handful of dried COOKSONIA stems — leafless, thinner than a pencil, \
each forking into two and then two again, tipped with tiny round spore capsules. \
Bleached pale and brittle from drying. Beside them a scatter of dark ash and one \
charred stem end.""",
    never="no trees, no logs, no branches, no leaves, no grass, no ferns, no flowers, no fruit, "
          "no seeds, no matches, no lighter, no fire pit, no cooked meat"),

"devonian": dict(
    cap="Fish, and the first seeds. The first food on Earth that keeps.",
    scene="""
THE FIRST FOOD THAT CAN BE STORED. On a slab of rough bark: a whole lobe-finned \
fish, thick-scaled and heavy-bodied with fleshy muscular fin bases, and beside it \
a small pile of EARLY SEEDS — hard, dry, teardrop-shaped kernels each partly \
enclosed in a ragged cupule of woody tissue, no bigger than a fingernail.

A few fern-like Archaeopteris fronds beneath as bedding. The seeds are the point: \
dry, dense and portable, they keep for months, and nothing before this era could \
be saved for later.""",
    never="no grass, no wheat, no grain ears, no flowers, no fruit, no nuts in shells, no "
          "conifer cones, no acorns, no modern fish, no cooked food, no bowl"),

"carboniferous": dict(
    cap="Freshwater fish, large insects, seed-fern seeds. The forest itself is inedible.",
    scene="""
THE MENU IS ENTIRELY ANIMAL PLUS A FEW SEEDS. On a sheet of scaly Lepidodendron \
bark showing its diamond-lattice leaf-scar pattern:

Two freshwater fish, silver-brown and slick. A large dark segmented insect with \
long membranous wings folded back. A small heap of seed-fern seeds, hard and \
brown. A short length of jointed Calamites stem, hollow and bamboo-like, which is \
fuel rather than food.

Nothing green is edible: the surrounding forest is lignin and cellulose.""",
    never="no grass, no flowers, no fruit, no berries, no nuts, no vegetables, no bread, "
          "no cooked food, no crab, no lobster, no shrimp, no conifer cones, no broadleaf leaves"),

"permian": dict(
    cap="Dried fish and tongue-shaped leaves you cannot digest. Thin, and getting thinner.",
    scene="""
A THIN AND FAILING LARDER. On cracked red desert clay: three strips of \
sun-dried, leathery, darkened fish, curled at the edges. A few small hard seeds. \
Several GLOSSOPTERIS leaves — distinctly tongue-shaped, broad at the tip and \
tapering to the stalk, with a strong central midrib and a fine net of secondary \
veins — which are fibrous and indigestible, present only to show that the plants \
here do not help.

Everything is dry, dusty and sparse. Grit has blown across the arrangement.""",
    never="no grass, no flowers, no fruit, no vegetables, no bread, no cactus, no succulents, "
          "no modern dried fish fillets, no salt, no bowl, no cooked food"),

"triassic": dict(
    cap="Cycad seeds. Bright, abundant, and they will destroy your liver.",
    scene="""
THE MOST DANGEROUS PLATE ON THIS LIST. On cracked pale mud: a cluster of large \
CYCAD SEEDS, each the size of a plum, with a smooth fleshy outer coat in warm \
orange-red over a hard stony inner shell, several split open to show the pale \
kernel inside. They look abundant, ripe and inviting.

Beside them one small dark lizard-like reptile and a scatter of dry Dicroidium \
seed-fern fronds, each frond forked into a distinctive Y shape.

The seeds are the subject. They are hepatotoxic and neurotoxic raw, and require \
days of soaking that nobody has worked out yet.""",
    never="no grass, no flowers, no fruit, no apples, no plums, no peaches, no berries, "
          "no nuts, no bread, no cooked food, no warning label, no skull symbol"),

"jurassic": dict(
    cap="Conifer needles, ginkgo seeds, a cycad cone. Not one item here is safely edible.",
    scene="""
A PLATE ON WHICH NOTHING IS SAFELY EDIBLE, AND THAT IS THE POINT. On damp forest \
litter:

A spray of stiff dark araucaria conifer foliage with small overlapping scale-like \
leaves. A few GINKGO leaves, unmistakably fan-shaped and split into two lobes, \
with a handful of pale fleshy ginkgo seeds that smell rancid. A broken CYCAD CONE, \
barrel-shaped and armoured with tight overlapping woody scales, spilling toxic \
seeds. Some tight coiled fern fiddleheads.

Everything is tough, resinous, bitter or poisonous. There is not one flower, one \
fruit or one grain anywhere in the world.""",
    never="no flowers, no blossom, no fruit, no berries, no apples, no grass, no wheat, "
          "no vegetables, no bread, no mushrooms, no meat, no cooked food, no palm fronds"),

"cretaceous": dict(
    cap="The first fruit on Earth. Small, fibrous, mostly seed, and nobody bred it for you.",
    scene="""
THE FIRST FRUIT IN EARTH'S HISTORY, lying on a bed of large glossy magnolia \
leaves on damp floodplain mud.

Small primitive figs, a cluster of fibrous palm drupes still on a short woody \
stalk, and a MAGNOLIA SEED CONE: a knobbly elongated aggregate structure studded \
with small bright red seeds emerging from splitting pods.

Everything is small, tough, fibrous and mostly seed rather than flesh — none of \
it has been bred by anyone for sweetness or size. A few freshwater mussel shells \
to one side.""",
    never="no apples, no oranges, no bananas, no grapes, no strawberries, no raspberries, "
          "no cherries, no melon, no tomato, no modern cultivated or orchard fruit, no grass, "
          "no wheat, no bread"),

"paleogene": dict(
    cap="Nuts, fruit, tubers, palm dates. The first complete diet available to a human.",
    scene="""
THE FIRST COMPLETE DIET ON THIS LIST. On a bed of large broadleaf litter and dark \
rich soil: a generous spread of hard-shelled nuts, several small dark fleshy \
fruits, a cluster of date-like palm drupes on a stalk, two knobbly earth-covered \
tubers with one broken open to show pale dense starchy flesh, and a scatter of \
seeds.

Abundant, varied and calorie-dense. For the first time the land alone can feed \
you.""",
    never="no grass, no wheat, no maize, no rice, no potatoes, no carrots, no modern orchard "
          "apples or oranges, no bananas, no bread, no cooked food, no basket, no bowl"),

"neogene": dict(
    cap="Grass seed, roots and game. Enormous work for very few calories.",
    scene="""
GRASS EXISTS NOW AND IT IS BARELY WORTH EATING. On dry cracked earth: several \
whole GRASS SEED HEADS on long dry stalks, the individual grains tiny, hard, \
tightly husked and scattering off the stem at a touch. A small pile of the loose \
grains beside them, obviously a poor return for the effort.

With them, two fibrous earth-covered roots and a portion of dark lean game meat.

The grains are minute compared to anything cultivated: this is wild grass, \
thousands of years before anyone selected it for bigger seed that stays on the \
stalk.""",
    never="no wheat ears, no barley, no cultivated cereal, no bread, no flour, no maize, "
          "no rice bowl, no fruit, no vegetables, no cooked food, no sickle, no basket"),

"quaternary": dict(
    cap="Everything at once. This is the diet your body was actually built for.",
    scene="""
THE DIET YOUR SPECIES WAS SHAPED BY. On a flat cold stone: cuts of dark red lean \
game meat, a cracked long bone with exposed marrow, a heap of small dark berries, \
several fibrous roots and tubers with soil still on them, a few hard nuts, and a \
whole freshwater fish.

Varied, fatty, seasonal and hard-won. Everything here is wild, and everything \
here is something a human body knows exactly what to do with.""",
    never="no bread, no cereal, no rice, no pasta, no cultivated vegetables, no modern cuts of "
          "butchered meat, no plate, no bowl, no knife, no cooking pot, no salt, no herbs"),
}


# ---------------------------------------------------------------------------
# KILLS — the air made visible, and what it is carrying.
# ---------------------------------------------------------------------------
KILLS = {
"hadean": dict(
    cap="Sulfurous vapour off molten rock. One breath is enough.",
    scene="""
THE AIR IS VENTING OUT OF THE GROUND. Ground-level detail of a glowing orange \
fissure in black basalt crust, with dense sulfurous vapour pouring upward out of \
it and rolling toward the camera. Heat distortion visibly warping everything \
above the crack. Yellow sulfur crusting the fissure lips. The vapour is thick \
enough to be the main mass in the frame."""),

"archean": dict(
    cap="Methane haze. It looks like a warm evening and there is no oxygen in it.",
    scene="""
THE AIR IS A THICK ORANGE PHOTOCHEMICAL HAZE, and it looks beautiful. Layered \
banks of dense orange organic smog drifting low over still shallow water, the sun \
reduced to a small dim featureless disc barely penetrating it. No blue anywhere. \
Everything more than a short distance away dissolves completely into the murk. \
Warm, calm, and completely unbreathable."""),

"proterozoic": dict(
    cap="Ice fog and diamond dust. The cold is the part you can see.",
    scene="""
THE AIR IS FULL OF SUSPENDED ICE. Dead-still frigid air over a white surface, \
filled with drifting ice fog and countless tiny suspended frost crystals catching \
the low sun as glittering points — diamond dust. Frost feathers growing on the \
ice in the foreground. Visibility closing to nothing within metres. Utterly \
silent and lethally dry."""),

"ediacaran": dict(
    cap="The medium is water. There is no version of this you can breathe.",
    scene="""
THE MEDIUM IS WATER AND YOU CANNOT BREATHE IT. Looking through a dim green-blue \
water column: suspended organic particles and marine snow drifting slowly through \
weak light shafts that attenuate and die within a few metres. The surface is \
visible far above as a faint pale shimmer, unreachable. Heavy, cold, pressing."""),

"cambrian": dict(
    cap="Dry wind over bare stone. Nothing organic in the air, and nothing to burn.",
    scene="""
THE AIR CARRIES NOTHING BUT ROCK DUST. A dry cold wind driving fine grey mineral \
dust and sand low across bare fractured bedrock, streaming in visible ribbons \
over the stone. Not one seed, spore, leaf fragment, insect or scrap of organic \
matter in the air, because none exists. Sterile, abrasive, and empty."""),

"ordovician": dict(
    cap="Cold spray and sleet on bare rock, with no fire anywhere on Earth.",
    scene="""
THE AIR IS FULL OF FREEZING WATER. Cold sea spray and driving sleet blowing \
horizontally across dark wet bare rock, the droplets caught mid-flight and \
streaking. A thin flat crust of dark liverwort on the stone, soaked. Grey, \
bitter, soaking, with nothing dry anywhere in the frame."""),

"silurian": dict(
    cap="The first smoke in Earth's history. Everything changes here.",
    scene="""
THE FIRST SMOKE THAT EVER ROSE FROM THIS PLANET. A single thin thread of pale \
grey-blue smoke rising from a small smouldering bundle of dried leafless \
Cooksonia stems on wet mud, the ember glowing faintly orange at its base. The \
smoke catches low sunlight as it curls upward. Small, quiet, and the most \
important thing in this entire sequence of images."""),

"devonian": dict(
    cap="Air thick with spores. Breathable at last, and still nothing to eat.",
    scene="""
THE AIR IS THICK WITH DRIFTING SPORES. Humid still forest air dense with \
countless pale spores and fine organic dust hanging suspended, lit by shafts of \
amber light raking between dark woody trunks. The particles are the subject: the \
air is visibly full of life and none of it is food."""),

"carboniferous": dict(
    cap="Embers riding 30% oxygen. Fire moves faster here than in air you have breathed.",
    scene="""
THE AIR IS CARRYING FIRE. Close ground-level detail of burning leaf litter and \
peat on a swamp margin: orange embers and glowing flakes of ash lifting off the \
ground and streaming upward through dense grey smoke. The flame front is low, \
fast and spreading across visibly damp material. Oxygen-rich air makes it burn \
hotter and travel faster than it should."""),

"permian": dict(
    cap="A dust storm crossing a continent with no coast to stop it.",
    scene="""
THE AIR HAS BECOME THE GROUND. The advancing wall of a dust storm, a dense \
rolling front of rust-orange dust filling most of the frame and blotting out \
everything behind it, streaming grit and sand across cracked red desert clay in \
the immediate foreground. The sun a hard pale disc barely visible through it."""),

"triassic": dict(
    cap="Thin hot air over cracked mud. Sea level here feels like 4,500 metres.",
    scene="""
THE AIR IS THIN AND HOT AND VISIBLY MOVING. Heavy heat shimmer rising off a floor \
of cracked pale mud, distorting everything above it into a wavering blur. Fine \
dust lifting in a small spiralling dust devil in the middle distance. The light \
is flat, washed out and dusty. Dead, dry and short of breath."""),

"jurassic": dict(
    cap="Fog between the trunks. The forest is full and none of it is edible.",
    scene="""
THE AIR IS DENSE WHITE FOG. Thick humid fog packed between dark straight conifer \
trunks, reducing everything beyond a few metres to grey silhouettes and swallowing \
the ground entirely. Moisture beading on bark and fern fronds in the immediate \
foreground. Close, muffled, disorienting, and something could be standing in it."""),

"cretaceous": dict(
    cap="Chicxulub. Ejecta re-entering, and the sky becomes a broiler.",
    scene="""
THE AIR IS ON FIRE. The sky filled edge to edge with hundreds of incandescent \
streaks of re-entering ejecta, glowing white-orange, raking down through smoke \
and dust. The whole atmosphere is lit from above with a hard infrared glow. \
Silhouetted magnolia leaves and palm fronds in the immediate foreground beginning \
to scorch and curl. Apocalyptic, and it lasted about an hour."""),

"paleogene": dict(
    cap="PETM steam. Air too wet to shed your own heat into.",
    scene="""
THE AIR IS SATURATED AND WILL NOT TAKE YOUR HEAT. Dense white steam and vapour \
rising off warm standing water and wet dark leaf litter in a hot swamp forest, \
hanging motionless between the trunks in thick humid layers. Condensation running \
off broad leaves. Heavy, oppressive, airless and utterly still."""),

"neogene": dict(
    cap="Dry-season smoke and dust. Grass burns, and it burns every year.",
    scene="""
THE AIR IS FULL OF SMOKE AND DRY DUST. Low golden light raking through drifting \
brown grass-fire smoke and suspended dust across open savanna, the individual \
particles catching the sun. Charred black stubble and ash in the near foreground, \
with tall dry bunch-grass beyond. Hot, gritty, and thick in the throat."""),

"quaternary": dict(
    cap="Whiteout. The cold is the only thing here that is actively trying to kill you.",
    scene="""
THE AIR HAS ERASED THE WORLD. A ground-level whiteout: wind-driven snow streaming \
horizontally in dense sheets, the horizon completely gone, visibility down to a \
few metres of frozen tussock grass in the immediate foreground. Spindrift curling \
off the drifts. Grey-white, featureless, and violently cold."""),
}

# The kills set shares one negative list — the failure mode there is a figure
# appearing in frame, not the wrong organism.
KILLS_NEVER = ("no people, no animals, no creatures, no faces, no skulls, no bones, no corpses, "
               "no vehicles, no machines, no campfire ring, no tents")


def build(kind: str, slug: str) -> str:
    """Assemble the full prompt for one image. `kind` is scene, menu or kills."""
    if kind == "menu":
        e = MENU[slug]
        return (f"{MENU_STYLE}\n{e['scene'].strip()}\n\n"
                f"DO NOT INCLUDE, these did not exist yet or are anachronistic: "
                f"{e['never']}.\nAlso: {NEVER}.")
    if kind == "kills":
        e = KILLS[slug]
        return (f"{KILLS_STYLE}\n\nPALETTE — hold the image within these colours and shades "
                f"between them: {PALETTES[slug]}\n{e['scene'].strip()}\n\n"
                f"DO NOT INCLUDE: {KILLS_NEVER}.\nAlso: {NEVER}.")
    raise ValueError(f"unknown set: {kind}")


def caption(kind: str, slug: str) -> str:
    """The page caption, rendered as HTML under the figure — never drawn into
    the image. The model renders lettering badly, and baked-in text cannot be
    selected, translated or read aloud."""
    return {"menu": MENU, "kills": KILLS}[kind][slug]["cap"]
