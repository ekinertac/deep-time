"""
prompts.py: the prompt data for episode 02, Centuries. No logic beyond assembly.

THE PREMISE, because every prompt depends on it. Twenty centuries, one city.
You arrive in Rome with the clothes you are wearing and a knife, once per
century, and the only thing that changes between visits is the date. Fixing the
place is what makes the twenty numbers comparable: if a verdict moves, the
century moved it, not a choice about where to stand.

You are immune to anything another person is carrying. Plague, smallpox,
measles, typhus, cholera, dysentery, influenza and tuberculosis cannot touch
you. Everything your own body and the ground can do to you is unchanged: a
wound going septic, a tooth abscess, appendicitis, tetanus out of the soil.
That rule is not a kindness. It removes the obvious answer and forces the real
one, and it inverts two centuries: the years that kill a third of Rome are the
years Rome is desperate enough to hire you.

THE THREE SETS, and why each looks the way it does:

 scene 21:9, full width, opens each century page. ONE VIEWPOINT, TWENTY TIMES:
     standing at the western end of the Roman Forum below the Capitoline,
     looking east down the Sacra Via toward the Colosseum. Every frame is
     that same view. The camera never moves in two thousand years, so the
     reader reads change rather than composition. This is the whole visual
     argument of the episode and it is why the prompts repeat the framing
     language verbatim: marble city, then looted shell, then pasture with
     cattle, then a quarry, then a dig site, then a fenced monument. The
     ground level itself rises about ten metres by the 1700s and comes back
     down in the 1800s, which is the single most legible thing in the series.

 menu  3:2, sits in "If you survive". Everything you would actually be given
     to eat that century, lying on the surface it was served on. Same
     forensic overhead register as episode 01: close, static, neutral
     daylight, evidence rather than food photography. The hard part here is
     not what to include but what to exclude. No tomato, potato, maize,
     chili, turkey, cocoa or vanilla before the 1500s, and none of them
     common in Rome much before the 1700s. No fork before the late Middle
     Ages. No distilled spirits before the 12th century. Getting this wrong
     is the anachronism that a reader will catch instantly.

 tag  3:2, sits in "What decides your fate". THE OBJECT THAT DECIDES WHAT YOU
     ARE. Episode 01 used this slot for the air, because six of its sixteen
     intervals killed with something invisible. Here the invisible thing is
     your legal status, so the slot holds the physical object that assigns
     it: an inscribed slave collar, a pilgrim's badge, a jubilee token, an
     inquisition summons, a ration book, an identity card. Shot as a museum
     object on a neutral surface, hard raking light, no hands, no wearer.
     Across twenty frames these objects tell the episode's argument on their
     own: property, then pilgrim, then papers.

Read alongside: ../tools/gen_img.py (the engine that consumes this), data.js
(the verdicts and vitals these images sit beside), ../deep-time/prompts.py (the
same file for episode 01, and the reason this one is shaped the way it is).
"""

# The three sets this episode has, mapping to output folder and aspect ratio.
SETS = {
  "scene": ("hero", "21:9"),
  "menu":  ("menu", "3:2"),
  "tag":   ("tag",  "3:2"),
}

# ---------------------------------------------------------------------------
# Style contracts. Byte-identical in every prompt of a set: this is what makes
# twenty separate generations read as one series rather than twenty pictures.
# ---------------------------------------------------------------------------

# The fixed viewpoint, repeated word for word in all twenty scene prompts. The
# model will not hold a camera position across separate calls unless it is
# restated every time, and the whole set fails if the camera wanders.
SCENE_STYLE = """Photorealistic cinematic view, film still shot on 65mm, wide 21:9 format. \
Naturalistic light, volumetric haze separating depth layers, sun low in the east. \
Desaturated and colour-graded, muted, restrained. Nothing neon or candy-coloured.

FIXED CAMERA, IDENTICAL IN EVERY IMAGE OF THIS SERIES: standing at the western \
end of the Roman Forum in Rome, on the ground, at the foot of the Capitoline \
hill, looking east-southeast straight down the length of the Forum valley toward \
the Colosseum in the far distance. Eye level, roughly 1.7 metres above whatever \
the ground surface happens to be. The Palatine hill rises along the right side of \
the frame, the lower slope of the Capitoline is behind the camera, the valley \
runs away into the distance in the centre. Horizon roughly a third from the \
bottom. Distinct foreground, midground and hazy far distance. This exact \
framing, every time."""

MENU_STYLE = """Photorealistic overhead still-life, 3:2 format, shot on 65mm macro \
lens looking straight down. Neutral north daylight, no colour grading, no mood \
lighting. Everything lies flat on the surface it was actually served or eaten \
on. Close, static, forensic: a specimen plate, evidence of a meal rather than \
an appetising photograph of one. Sharp throughout, no shallow depth of field, no \
styling, no garnish, no cloth arranged for effect."""

TAG_STYLE = """Photorealistic museum object photograph, 3:2 format, shot on 65mm at \
a slight angle from above. ONE OBJECT IS THE SUBJECT and it fills most of the \
frame. Hard raking light from one side so that every scratch, corrosion pit, \
tool mark and worn edge reads. Neutral grey-brown surface underneath, no props, \
no background clutter, no hands, no person wearing or holding it. The object is \
used and worn, not a replica and not newly made. Desaturated, muted, restrained."""

# Applied to every prompt in every set. These are failures of the medium rather
# than failures of the century.
NEVER = ("no text overlay, no captions, no letters added by the renderer, no numbers, "
         "no watermark, no signature, no border or frame, no lens flare, "
         "no split screen, no collage, no before-and-after comparison")

# The tag set shares one negative list: the failure mode is a person entering
# the frame, not the wrong object.
TAG_NEVER = ("no people, no hands, no fingers, no faces, no mannequin, no body, "
             "no one wearing the object, no shop display, no price tag, "
             "no modern packaging, no plastic, no studio softbox reflections")

SLUGS = [
  "01-first", "02-second", "03-third", "04-fourth", "05-fifth",
  "06-sixth", "07-seventh", "08-eighth", "09-ninth", "10-tenth",
  "11-eleventh", "12-twelfth", "13-thirteenth", "14-fourteenth", "15-fifteenth",
  "16-sixteenth", "17-seventeenth", "18-eighteenth", "19-nineteenth", "20-twentieth",
]

# One colour identity per century, mirroring that century's block in
# assets/centuries.css so a generated image lands inside the page theme. The arc
# is deliberate and slow: imperial marble and gold, cooling through late antique
# brick into medieval mud and smoke, warming again through Renaissance stone and
# Baroque gilt, then the grey of an excavated modern city.
PALETTES = {
  "01-first":       "#e8dcc4 #c9a227 #7a6a52 #2b241a",
  "02-second":      "#e2d4b8 #bf9526 #6f6049 #261f17",
  "03-third":       "#cdbb9c #a8761f #5c5142 #201a14",
  "04-fourth":      "#c3b094 #96682a #4f4639 #1c1712",
  "05-fifth":       "#b09a7d #85552b #453d33 #191410",
  "06-sixth":       "#9a866c #6f4529 #3c352d #16120f",
  "07-seventh":     "#8d7c66 #63402a #38312a #15110e",
  "08-eighth":      "#8a7a67 #5d3f2b #362f29 #141110",
  "09-ninth":       "#84745f #58392a #332d27 #131010",
  "10-tenth":       "#7e6f5c #523528 #302a25 #12100f",
  "11-eleventh":    "#836f58 #6b3320 #322a24 #131010",
  "12-twelfth":     "#8a7659 #6d3b22 #342c25 #141110",
  "13-thirteenth":  "#9a8462 #7d4d24 #3a3128 #16130f",
  "14-fourteenth":  "#8f8168 #6a5a30 #38332a #151310",
  "15-fifteenth":   "#b5a37e #8e6b2c #4a4134 #1a1712",
  "16-sixteenth":   "#c4b189 #9c6f2d #524734 #1c1813",
  "17-seventeenth": "#cbb68d #ab7a2c #574a36 #1e1a14",
  "18-eighteenth":  "#cdba97 #a8802f #5a4d3a #201c16",
  "19-nineteenth":  "#b8ae9c #8a7440 #4e4a42 #1c1a17",
  "20-twentieth":   "#aaa9a4 #7d7259 #48474a #17171a",
}

# ---------------------------------------------------------------------------
# THE SCENE SET. One camera position, twenty dates. Each entry restates the
# framing through SCENE_STYLE and then describes only what has changed, because
# what has changed is the entire argument. `never` names what did not exist yet
# or no longer existed, which is the part a general image model gets wrong by
# default: it will happily put a bell tower in the year 50 and a marble city in
# the year 950 unless it is told not to.
# ---------------------------------------------------------------------------
SCENE = {

"01-first": dict(scene="""
Rome at the height of the empire, around the year 80. The Forum is complete, \
crowded and in full use. Every surface is dressed marble and travertine, white \
and honey-coloured, still sharp-edged. Gilded bronze roof tiles and gilded \
statues catch the low sun. Rows of columns down both sides, painted and gilded \
detail on the entablatures, bronze equestrian statues on high bases lining the \
central pavement. Purple and white awnings. The paving is swept and level.

People everywhere: togas, tunics, litters carried by slaves, market stalls at \
the margins, a dense civic crowd going about business.

In the far distance the Colosseum, newly finished, its outer arcades filled with \
statues and its travertine still pale and unweathered.""",
  never="no ruins, no rubble, no broken columns, no weeds or grass growing in the "
        "paving, no vegetation on any building, no churches, no crosses, no bell "
        "towers, no domes, no triumphal arch at the near western end of the Forum, "
        "no enormous brick vaults on the north side, no cattle, no huts, no timber "
        "shacks, no medieval towers"),

"02-second": dict(scene="""
Rome at its absolute peak, around the year 150. The same view, denser and richer \
than fifty years before. New marble temples have filled the remaining gaps along \
the north side, their columns cipollino green and pavonazzetto purple-veined. \
Freshly gilded bronze doors. More statues than there is room for, standing \
shoulder to shoulder on their bases.

A great domed and vaulted temple on the rise at the east end of the valley, \
enormous, new, its bronze tiles blinding in the sun.

A civic crowd of a million-person city: dense, busy, unremarkable to itself.""",
  never="no ruins, no rubble, no broken columns, no weeds, no vegetation on "
        "buildings, no churches, no crosses, no bell towers, no triumphal arch at "
        "the near western end of the Forum, no enormous brick vaults on the north "
        "side, no cattle, no huts, no medieval towers, no scaffolding"),

"03-third": dict(scene="""
Rome around the year 280, still monumental and visibly no longer growing. A tall \
new triumphal arch in white marble stands close to the camera at the western end, \
its reliefs crisp and deeply undercut, the newest thing in sight.

Behind it the older buildings are patched rather than replaced: fire-blackened \
stone on one flank, mismatched columns reused from somewhere else, statue bases \
recut with new inscriptions over old ones. The marble is grey with soot in the \
sheltered corners.

Fewer people than a century ago, and more soldiers among them.""",
  never="no ruins in collapse, no weeds in the paving, no churches, no crosses, no "
        "bell towers, no enormous brick vaults on the north side, no cattle, no "
        "huts, no medieval towers, no scaffolding, no abandoned buildings"),

"04-fourth": dict(scene="""
Rome around the year 350, monumental and quietly emptying. Along the north side, \
three colossal brick-and-concrete vaults now loom over everything, coffered inside, \
the largest roofed space in the world and utterly out of scale with the marble \
temples beside them.

The temples are shut. Their doors are closed and their steps are clean but unused. \
Statues stand in rows, though gaps have appeared where some have been taken away.

Near the Colosseum in the far distance, a second triumphal arch. The crowd is \
thinner and better wrapped against the cold.""",
  never="no ruined vaults, no collapse, no weeds in the paving, no bell towers, no "
        "cattle, no huts, no medieval towers, no vegetation growing on buildings, "
        "no market stalls filling the central space, no scaffolding"),

"05-fifth": dict(scene="""
Rome around the year 460, fifty years after the first sack and five after the \
second. The buildings still stand and are visibly stripped. Roofs are missing \
their bronze and lead, showing bare timber. One long basilica on the north side \
is a burnt shell, its roof gone, its marble floor scorched.

Statue bases stand empty, their bronzes carried off. Grass has started in the \
joints of the paving and along the steps. Shutters and boards over doorways.

A handful of people crossing a space built for tens of thousands. In the far \
distance the Colosseum, intact, unused.""",
  never="no total ruin, no collapsed walls, no cattle grazing, no huts, no medieval "
        "towers, no bell towers, no scaffolding, no trees growing out of masonry, "
        "no dense crowd, no market"),

"06-sixth": dict(scene="""
Rome around the year 550, during the Gothic wars, with the aqueducts cut and the \
city besieged five times in twenty years. The buildings are still standing and \
almost nobody is there.

Grass and weeds through every joint in the paving. Fallen roof tiles and rubble \
drifted against the column bases. Siege damage: a wall breached and crudely \
blocked with rubble, timber props. A dead silence to the space.

Two or three figures, small in the frame, crossing quickly. Smoke from one \
cooking fire somewhere among the colonnades. Overcast, cold, still.""",
  never="no crowds, no market, no cattle herds, no medieval towers, no complete "
        "collapse into mounds, no forest, no bell towers, no intact gilded statues, "
        "no bright sunlight, no snow"),

"07-seventh": dict(scene="""
Rome around the year 650. A single new column has been raised in the middle of the \
open space, taller than a house, carrying a statue: the last monument anyone will \
ever erect here.

The old senate house on the left has been made into a church, a cross fixed above \
its bronze doors. So has a temple on the north side, its portico now a porch. \
Elsewhere the marble is being taken: a lime kiln smokes at the edge of the frame, \
column drums stacked beside it waiting to be burned into mortar.

Vegetable plots in the corners. Grass over most of the paving. Perhaps thirty \
thousand people left in the whole city.""",
  never="no crowds, no intact marble city, no statues in rows, no cattle herds "
        "filling the space, no tall medieval defensive towers, no domes, no "
        "Renaissance buildings, no vineyard covering the whole valley"),

"08-eighth": dict(scene="""
Rome around the year 760. The valley is half quarry and half garden. Two lime \
kilns smoking. Ancient marble stacked, split and carted. Gaps where whole \
porticoes have simply been removed.

Small churches occupy the old shells, with plain campanile bell towers in brick, \
the newest structures in view. Vegetable gardens and vine rows on the terraces. \
Dirt tracks worn diagonally across what was once formal paving, taking the short \
route rather than the ceremonial one.

Pilgrims walking east in ones and twos with staffs and satchels.""",
  never="no crowds, no intact marble city, no statues on bases, no fortified stone "
        "towers, no Renaissance buildings, no domes, no cattle market, no dense "
        "housing, no paved road surface"),

"09-ninth": dict(scene="""
Rome around the year 870, twenty years after an earthquake. Sections of colonnade \
have come down and lie where they fell, drums scattered like dropped coins. Cracks \
run through standing walls, some braced with timber and brick.

Brick bell towers with small arched windows stand over the churches built into \
ancient shells. Soil is visibly deepening over the old pavement: a metre of it in \
places, with grass, thistles and a few young trees rooted in the rubble.

Goats. A cart track. Two pilgrims. Everything else is empty.""",
  never="no intact marble city, no crowds, no market, no fortified stone tower "
        "houses, no Renaissance domes, no dense housing, no cattle market, no "
        "excavation, no formal gardens"),

"10-tenth": dict(scene="""
Rome around the year 970, at its emptiest. The valley reads as rough pasture with \
ruins in it rather than as a city. Deep grass, brambles, thorn scrub, standing \
water in the low ground because nothing drains any more.

Column stumps and fragments of entablature protrude from the turf at odd angles, \
half-buried. Two or three brick campanili are the only maintained structures in \
sight. A cow track worn through the middle.

Cattle grazing among the marble. A shepherd. Low grey light, mist in the valley.""",
  never="no intact buildings other than small churches, no crowds, no market, no "
        "fortified towers, no Renaissance buildings, no domes, no excavation, no "
        "formal avenues of trees, no paved surface"),

"11-eleventh": dict(scene="""
Rome around the year 1090, six years after the Norman fire that burned this \
quarter. A burnt zone: blackened walls, scorched marble spalled white and grey, \
roof timbers reduced to charcoal, whole blocks abandoned and roofless.

Nothing has been rebuilt. Weeds are already back through the ash. A single \
church repaired with mismatched brick stands among it.

At the far end, the first crude fortifications: an ancient arch crudely walled up \
and built over with rubble masonry to make a strongpoint, arrow slits knocked \
through Roman stone.""",
  never="no intact marble city, no crowds, no market, no Renaissance buildings, no "
        "domes, no formal gardens, no excavation, no cattle market, no tall slender "
        "Gothic architecture, no stone tracery windows"),

"12-twelfth": dict(scene="""
Rome around the year 1160, a city of private armies. Square brick tower houses \
rise out of the ruins, tall, narrow, windowless at the base, built directly on \
top of and into ancient masonry. One clamps around a Roman triumphal arch and \
uses it as a gatehouse.

Between them, pasture and vegetable plots on deep soil that has buried the old \
pavement entirely. Rubble walls partition the valley into holdings.

A cart, some goats, armed men on a roofline. Nothing monumental is being \
maintained and nothing is being cleared.""",
  never="no intact marble city, no crowds, no Renaissance buildings, no domes, no "
        "formal avenues, no excavation, no Gothic cathedral, no stone tracery, no "
        "cannon, no firearms, no glazed shop windows"),

"13-thirteenth": dict(scene="""
Rome around the year 1300, in a jubilee year. The valley is pasture and the road \
through it is packed: a continuous slow file of pilgrims crossing east on foot, \
staffs, packs, wide hats, thousands of them, worn into a wide muddy track.

Improvised stalls along the route selling bread and badges. Tower houses on both \
sides. The Colosseum at the far end, part fortress, part quarry, with rubble \
filling its lower arcades.

Cattle in the middle distance ignoring all of it. The ground level is now well \
above the old paving; arches stand in the earth up to their springing.""",
  never="no intact marble city, no Renaissance buildings, no domes, no excavation, "
        "no formal tree avenues, no firearms, no printed paper, no glazed windows, "
        "no carriages with springs, no cobbled formal road"),

"14-fourteenth": dict(scene="""
Rome around the year 1370, with the papacy gone to France and perhaps seventeen \
thousand people left in the whole city. This is the cow field. Long unkempt grass \
across the entire valley, cattle grazing in loose groups, a herdsman.

Column stumps and the tops of arches stand out of the turf at random. One \
freestanding row of three columns, half-buried, no building attached. Fresh \
earthquake damage on the Colosseum: a long section of its outer ring collapsed \
into a rubble slope.

Warm late light, dust, insects, complete pastoral quiet where a capital used to \
be.""",
  never="no crowds, no city, no market, no Renaissance buildings, no domes, no "
        "excavation, no formal tree avenues, no scaffolding, no intact marble "
        "buildings, no firearms"),

"15-fifteenth": dict(scene="""
Rome around the year 1470, being carted away. The pasture is now also a working \
quarry: scaffolding lashed around a standing ruin, men with crowbars, block and \
tackle, a windlass, oxcarts loaded with cut marble and column drums heading out of \
frame west.

Two lime kilns burning, white smoke, stacks of broken statuary waiting beside \
them. Deep ruts through the turf. Cattle still grazing between the workings.

The stone is not being destroyed so much as recycled: it is going to build the \
new churches and palaces on the other side of the river.""",
  never="no intact marble city, no crowds of citizens, no Baroque church facades, "
        "no formal avenues of elm trees, no excavation trenches, no archaeologists, "
        "no great dome on the skyline, no carriages, no street lighting"),

"16-sixteenth": dict(scene="""
Rome around the year 1570. The valley is a working cattle market: pens of rough \
timber hurdles, herds standing in churned mud, drovers, dung, flies.

On the right, the Palatine slope has become a formal terraced garden with clipped \
hedges, cypresses, an ornamental gateway and retaining walls, private and orderly \
directly above the mess below.

The ground level has risen enough that the great arch at the near end is buried to \
above its lower cornice and the surviving column shafts stand in the earth like \
posts. A large dome is visible far off over the rooftops behind.""",
  never="no excavation, no archaeological trenches, no fenced paths, no signage, no "
        "modern crowds of tourists, no carriages with glass windows, no gas lamps, "
        "no avenue of elm trees down the middle, no intact ancient buildings"),

"17-seventeenth": dict(scene="""
Rome around the year 1680. Two straight rows of young elm trees have been planted \
down the length of the cattle field, turning it into a formal avenue with cows \
still standing in it.

Baroque church fronts in travertine, curved and heavy, have been fitted onto the \
ancient shells: scrolled volutes, a small dome, a clock. They face a livestock \
market.

Everything ancient is deeper still: capitals at ankle height, whole arches sunk to \
their haunches. Carriages on the track, a religious procession crossing the \
avenue.""",
  never="no excavation, no archaeological trenches, no fenced monuments, no signage, "
        "no gas lamps, no electric light, no railings, no tourists with sketchbooks "
        "in large numbers, no intact ancient marble city"),

"18-eighteenth": dict(scene="""
Rome around the year 1770, at the height of the Grand Tour. The elm avenue is \
mature and shading the cattle market. Buried monuments stand in the raised earth: \
the great triumphal arch is sunk to roughly half its height, and people sit on its \
lower cornice at ground level.

Foreign gentlemen in coats and tricorne hats, sketchbooks, a portable easel, a \
local guide gesturing. Beggars. Cows and a scattering of goats between the tree \
trunks.

Warm dusty afternoon light, ruins picturesque and unmanaged, ivy where nobody has \
pulled it off.""",
  never="no excavation trenches, no spoil heaps, no railings or fences around "
        "monuments, no signage, no gas lamps, no electric light, no cameras, no "
        "motor vehicles, no bicycles, no clean archaeological park"),

"19-nineteenth": dict(scene="""
Rome around the year 1880, being dug out. Open excavation across the whole valley: \
deep trenches with battered earth sides, timber shoring, plank walkways, wheel-\
barrows on planks, spoil heaps, labourers in shirtsleeves with picks and baskets.

Monuments that stood buried to their waists now stand clear at the bottom of \
cuttings, the earth removed from around them, their bases exposed for the first \
time in a thousand years. Surveyors with instruments. The elms are gone.

Iron railings appearing around the cleared sections. Gas lamps on the road at the \
edge.""",
  never="no motor vehicles, no buses, no electric street lighting, no tarmac, no "
        "modern tourist crowds, no cattle market, no elm avenue, no cranes, no "
        "concrete, no high-visibility clothing, no modern signage"),

"20-twentieth": dict(scene="""
Rome around the year 1970. A fully excavated archaeological park, ten metres below \
the surrounding street level, everything cleared to the ancient pavement.

Gravel paths, low iron railings, small metal signs, umbrella pines and cypresses \
planted along the edges. Tourists in ones and threes with cameras and guidebooks. \
Brick stubs and column bases laid out and labelled.

A broad modern road runs along the north edge above the cutting with cars and a \
bus on it. Apartment rooflines, television aerials and street lighting on the \
skyline behind. Hot flat midday light.""",
  never="no cattle, no market, no excavation in progress, no spoil heaps, no elm "
        "avenue, no buried monuments, no ruins covered in earth, no horses and "
        "carts as the main traffic, no gas lamps"),

}

# ---------------------------------------------------------------------------
# THE MENU SET. What you would actually be handed to eat, on the surface it was
# handed to you on. `never` here is doing more work than in episode 01: the New
# World foods are the anachronism a reader spots instantly, and a general image
# model will put tomatoes on a Roman table every single time unless stopped.
# ---------------------------------------------------------------------------
MENU = {

"01-first": dict(scene="""
A slave's daily ration in imperial Rome, laid on a coarse red-brown terracotta \
plate on a plank table. A round flat loaf of dark emmer bread, torn open. A small \
heap of black olives. A wedge of hard sheep's cheese. A shallow dish of grey-brown \
fermented fish sauce. A rough clay cup of thin sour wine cut with water. A handful \
of dried figs.

Everything plain, unstyled, and slightly less than enough.""",
  never="no tomato, no potato, no maize or corn, no chili, no peppers, no turkey, "
        "no chocolate, no vanilla, no sugar, no pasta, no rice, no citrus, no fork, "
        "no glass drinking vessel, no printed label, no modern crockery",
  cap="Bread, olives, cheese, fish sauce, sour wine. A ration, and you are not on the list."),

"02-second": dict(scene="""
The bread dole and what a working man adds to it, on a wooden board. A large round \
loaf stamped with a baker's mark. A bowl of boiled lentils with a slick of olive \
oil. Salt pork. Boiled cabbage and leeks. A clay cup of watered wine. Olives, and \
a small dish of fish sauce for salt.

Filling, monotonous and rationed by a register you are not written into.""",
  never="no tomato, no potato, no maize, no chili, no peppers, no turkey, no "
        "chocolate, no sugar, no rice, no citrus, no fork, no glass vessel, no "
        "modern crockery, no printed label, no pasta",
  cap="The grain dole, plus whatever you can buy. You are not on the register."),

"03-third": dict(scene="""
A poor meal in a century of collapsing money, on a chipped earthenware plate. A \
small dark loaf, denser and coarser than before, with visible bran and grit. \
Boiled broad beans. A little salt fish, dried hard. Two onions. A cup of vinegary \
wine.

Beside the plate, three small copper-coloured coins with the silver wash worn off \
them, which is the point: the coin buys less bread every month.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no banknote, no printed label",
  cap="Less bread, worse bread, and coins that buy less of it every month."),

"04-fourth": dict(scene="""
A Christian charity distribution, laid on a plain wooden trestle. Round loaves \
stacked. A jar of olive oil. A cut of salt pork. Beans. A cup of wine.

Everything is identical and portioned: this is food handed out by an institution \
rather than bought, and the sameness of the portions is what says so.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no printed label, no plastic",
  cap="An institution feeds you now. Identical portions, handed out, not bought."),

"05-fifth": dict(scene="""
Thin food in a stripped city, on a worn wooden bowl and board. Coarse grey bread \
with visible bran. Boiled greens. A little hard cheese. Broad beans. Water in a \
plain cup rather than wine.

Less oil than any plate before it, because the shipping that brought it has \
stopped.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no abundance, no meat joint",
  cap="Grey bread and greens. The oil is thin because the ships have stopped."),

"06-sixth": dict(scene="""
Siege food, on bare stone. A handful of boiled nettles, dark green and limp. \
Acorns. Bran and chaff pressed into a flat grey cake. A strip of dark stringy \
meat that is clearly not from a farm animal. A cup of cloudy water.

Nothing here is food in the ordinary sense. It is what was left when the \
aqueducts were cut and the mills stopped turning.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no bread "
        "loaf, no cheese, no wine, no abundance",
  cap="Nettles, acorns, bran cake. Rome ate this for two years and wrote it down."),

"07-seventh": dict(scene="""
A pilgrim's dole at a church door, on a plain wooden trencher. A round loaf. A \
bowl of bean pottage with a little oil. A wedge of cheese. A cup of rough wine. \
A few onions and a bunch of greens from a garden plot.

Simple, sufficient and free, which is the whole point of it.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no printed label, no elaborate dish",
  cap="Bread, beans, cheese, wine. Free, because feeding strangers is the trade here."),

"08-eighth": dict(scene="""
What the hospices give and the gardens add, on a wooden board. A dark round loaf. \
Bean pottage. Roast chestnuts, some split open. Two eggs. Hard cheese. A cup of \
wine. A bunch of herbs.

Peasant food in a ruined capital, and more of it than the two centuries before.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no elaborate dish, no printed label",
  cap="Bread, beans, chestnuts, eggs. The gardens in the ruins are feeding people."),

"09-ninth": dict(scene="""
An ordinary meal in a small city, on rough pottery. A dark loaf. Broad beans \
cooked with oil. Boiled cabbage. Salt fish. A wedge of hard cheese. A cup of \
wine.

Nothing has improved and nothing has got worse. The plate is the same as a \
hundred years ago, which is itself the fact.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no elaborate dish, no printed label",
  cap="The same plate as a hundred years ago. That flatness is the century."),

"10-tenth": dict(scene="""
Subsistence, on a worn wooden board. A small dark loaf. Sheep's milk cheese. \
Boiled greens. Chestnuts. Broad beans. A cup of thin wine. No meat at all.

The food of about thirty thousand people living inside walls built for a \
million.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no meat, no elaborate dish",
  cap="Bread, cheese, chestnuts, greens. No meat, and no reason to expect any."),

"11-eleventh": dict(scene="""
A meal in a burnt quarter, on a cracked wooden bowl. Coarse bread. Bean pottage. \
A little salt pork. Onions. A cup of wine.

There is ash on the rim of the bowl and the bread is baked in an oven that was \
rebuilt in a hurry.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no elaborate dish, no abundance",
  cap="Bread, beans, salt pork, and ash on the rim of the bowl."),

"12-twelfth": dict(scene="""
What a labourer eats in a city of private towers, on a plain trencher. A round \
loaf. Bean and cabbage pottage. Hard cheese. Salt fish. Figs. A cup of wine.

Held in the hand rather than set on a table, because there is nowhere settled to \
sit.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus, no pasta, no fork, no glass vessel, no modern "
        "crockery, no elaborate dish, no printed label",
  cap="Bread, pottage, cheese, salt fish. Eaten standing up."),

"13-thirteenth": dict(scene="""
Pilgrim fare in a jubilee year, on a wooden board. A round loaf. Hard cheese. \
Dried figs. Salt fish. A cup of wine. Cooked beans in a small bowl. A hard-boiled \
egg.

Bought at a stall rather than given at a door, and priced for a market where two \
hundred thousand strangers arrived this year.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus fruit, no pasta, no fork, no glass vessel, no "
        "modern crockery, no printed label",
  cap="Bread, cheese, figs, salt fish. Sold, not given: two hundred thousand came this year."),

"14-fourteenth": dict(scene="""
A survivor's meal after the plague, on a wooden board. A good white loaf, better \
milled than any bread on the previous plates. A joint of roast mutton. Cheese. \
Broad beans. Onions. A generous cup of wine.

Better food than a labourer could have afforded before 1348. That is not \
prosperity, it is a labour shortage.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "sugar, no rice, no citrus fruit, no fork, no glass vessel, no modern "
        "crockery, no printed label, no poverty, no scraps",
  cap="Mutton and white bread. Not prosperity: a third of the workforce is dead."),

"15-fifteenth": dict(scene="""
A working man's meal in a rebuilding city, on a glazed earthenware plate. Fresh \
pasta, thick irregular strands, dressed with cheese and black pepper. A cut of \
pork. Artichokes trimmed and boiled. White bread. Almonds. Wine in a green glass \
flask.

The first plate in this series that a modern Roman would recognise as Roman \
food.""",
  never="no tomato, no potato, no maize, no chili, no turkey, no chocolate, no "
        "vanilla, no coffee, no dried pasta in a packet, no printed label, no "
        "modern crockery, no stainless steel",
  cap="Pasta, cheese, pepper, artichokes. The first plate a modern Roman would recognise."),

"16-sixteenth": dict(scene="""
A better table in the century of the sack and the Inquisition, on glazed \
majolica. Pasta with cheese and pepper. Roast pork. Artichokes. White bread. \
Oranges. Almonds and raisins. Wine in a glass.

In one corner, a single tomato, small, ribbed, dull red, sitting apart from the \
food because nobody eats it yet: it arrived as a curiosity and is grown for \
looking at.""",
  never="no tomato in any dish or sauce, no potato, no maize, no chili, no chocolate "
        "drink, no coffee, no modern crockery, no stainless steel, no printed label, "
        "no plastic, no red pasta sauce",
  cap="A tomato sits apart from the food. It has arrived, and nobody eats it yet."),

"17-seventeenth": dict(scene="""
A Baroque-era working meal, on plain glazed earthenware. Pasta with cheese and \
pepper. Boiled beef. Chicory and other bitter greens. White bread. A wedge of \
cheese. Wine in a glass tumbler. A few olives.

Ordinary, adequate, unremarkable. The most boring plate in the set, and the \
first one you could live on indefinitely.""",
  never="no tomato sauce, no red sauce on the pasta, no potato, no maize, no chili, "
        "no coffee cup, no modern crockery, no stainless steel, no printed label, "
        "no plastic, no restaurant plating",
  cap="Pasta, beef, bitter greens, bread. Dull, adequate, and survivable indefinitely."),

"18-eighteenth": dict(scene="""
Rome when the economy is foreigners, on white glazed earthenware. Pasta dressed \
with cheese and pepper. Roast lamb. Artichokes. Bread. A small cup of black \
coffee. Wine. A dish of tomatoes, cooked, unmistakably now part of the meal.

Two plates, in fact: the cheap one and the one a visiting Englishman is charged \
four times as much for.""",
  never="no potato as a staple, no maize polenta as the main dish, no chili, no "
        "modern crockery, no stainless steel cutlery, no printed label, no plastic, "
        "no restaurant plating, no photograph or postcard in frame",
  cap="Coffee, and tomatoes finally in the food. Also two prices, one for you."),

"19-nineteenth": dict(scene="""
Roman cooking as it settles into its modern form, on chipped white earthenware. \
Pasta with tomato sauce. Oxtail stewed with celery. Tripe. Artichokes. Coarse \
bread. A carafe of white wine. Pecorino.

The offal is the point: this is the fifth quarter, what was left after the good \
meat went to the households that could pay.""",
  never="no maize polenta as the main dish, no chili, no stainless steel, no plastic, "
        "no printed packaging, no restaurant plating, no photograph in frame, no "
        "electric appliance, no aluminium",
  cap="Pasta with tomato, oxtail, tripe. The fifth quarter: what was left after the good cuts."),

"20-twentieth": dict(scene="""
Two meals on one surface, divided by twenty years. On the left, a wartime ration \
of 1944: a small dark loaf of adulterated bread, a few chestnuts, a spoon of \
powdered egg, a thin soup. On the right, an ordinary plate from the 1970s: pasta \
with tomato and pecorino, artichokes, bread, a glass of wine, an orange.

The same city, the same street, one lifetime apart.""",
  never="no chili, no restaurant plating, no food styling, no plastic packaging with "
        "modern branding, no photograph in frame, no supermarket labels, no "
        "smartphone, no barcode",
  cap="A 1944 ration and a 1970s plate. Same city, same street, one lifetime apart."),

}

# ---------------------------------------------------------------------------
# THE TAG SET. The object that decides what you are. Read in order, these twenty
# frames make the episode's argument without a word of prose: property, then
# pilgrim, then papers.
# ---------------------------------------------------------------------------
TAG = {

"01-first": dict(scene="""
A Roman wax tablet diptych: two rectangular wooden leaves hinged together, the \
inner faces recessed and filled with dark beeswax, cursive Latin scratched into \
the wax with a stylus. The bronze stylus lies beside it. Wooden edges worn \
smooth and greasy from handling, one corner chipped.

This is a bill of sale for a person.""",
  cap="A sale contract on wax. In this century you are the thing being described."),

"02-second": dict(scene="""
A small bronze token, roughly the size of a coin but thicker and cruder, cast \
rather than struck, with a worn device on one face. Dark green patina in the \
recesses, rubbed bright on the raised surfaces from years in a pocket.

Entitlement to the free grain, issued to a name on a register.""",
  cap="A grain-dole token. Bread is free here, for the names on the list."),

"03-third": dict(scene="""
An iron branding iron: a long tapering shaft with a small shaped head, the \
working face formed into letters in relief. Heavy scale and rust over the shaft, \
the head burnt black and pitted, the handle end worn.

Used on livestock and on people who had run away from their owners.""",
  cap="A branding iron. Property that walks away has to be made identifiable."),

"04-fourth": dict(scene="""
A late Roman slave collar: a plain iron ring band, hinged, sized for a human \
neck, heavily corroded with red-brown rust, with a flat bronze disc riveted to \
it. The disc carries a crudely punched Latin inscription and a loop for a chain.

Objects like this survive in some number. The inscriptions ask whoever finds the \
wearer to return them.""",
  cap="An inscribed neck ring. The text on the disc is a return address."),

"05-fifth": dict(scene="""
A sheet of parchment, stiff, yellowed and cockled, with a list of names written \
in a small dark late-antique hand in two columns, some entries struck through. \
The edges are worn soft and one corner is torn away.

The register of the poor a church has agreed to feed.""",
  cap="The list of poor a church will feed. Being written on it is the whole trick."),

"06-sixth": dict(scene="""
A lead seal, small, thick and roughly circular, struck on both faces with a \
blurred monogram, still attached to a short length of frayed cord. The lead is \
dull grey-white with corrosion blooms, the impression soft and partly \
illegible.

Authority in a besieged city, reduced to a lump of metal on a string.""",
  cap="A lead seal on a cord. Authority, when there is not much left of it."),

"07-seventh": dict(scene="""
A pilgrim's ampulla: a small flattened lead-tin flask with two tiny handles and \
a narrow neck, stamped on one face with a simple standing figure in low relief. \
Grey-white metal, dented, one handle broken off, the stamped image half worn \
away.

Carried holy oil from a martyr's shrine, and marked the carrier as a pilgrim.""",
  cap="A shrine flask. The first object here that protects you instead of owning you."),

"08-eighth": dict(scene="""
A pilgrim's leather scrip and staff: a small worn satchel of thick dark leather \
with a long shoulder strap, the flap scuffed pale at the fold, lying beside the \
top third of an ash staff with an iron ferrule and a hand-polished grip.

Issued and blessed at departure. Carrying these made you a recognised category \
of person across the whole of Latin Europe.""",
  cap="Satchel and staff, blessed at departure. This is a legal status you can wear."),

"09-ninth": dict(scene="""
A papal lead bulla: a thick disc of dull grey lead struck on both faces, one \
with two crude bearded heads, the other with a name in Latin capitals, pierced \
by a cord channel with the remains of a hemp cord through it. Edges irregular \
from the striking.

Attached to documents that made a claim official.""",
  cap="A lead seal, pierced for a cord. It made a document true."),

"10-tenth": dict(scene="""
A tally stick: a length of split hazel, the two halves laid side by side, with a \
series of notches of different widths cut across both so the halves only match \
each other. Weathered grey, grubby at the handling ends.

A debt, a bread allowance, or a season's work, recorded by a population that \
mostly cannot read.""",
  cap="A split tally stick. Two halves that only match each other, and no writing."),

"11-eleventh": dict(scene="""
An iron manacle: a hinged wrist ring with a heavy hasp and a crude lock, thick \
with red-brown corrosion, a short length of chain still attached, the links \
uneven from hand forging. The inner surface is polished smooth where it turned \
against a wrist.

Taking captives was a normal part of a successful sack.""",
  cap="A wrist iron, polished smooth on the inside. Sacks produced captives, not just corpses."),

"12-twelfth": dict(scene="""
A large hand-forged iron key: a long shank with a simple ward pattern cut into \
the bit and a rough oval bow, hammer marks visible along the shaft, black with \
age and greasy at the bow from handling.

Belonging in this century means being on the inside of a particular door when \
the fighting starts.""",
  cap="A tower key. Belonging is now a question of which door closes behind you."),

"13-thirteenth": dict(scene="""
A pilgrim badge: a small flat openwork casting in dull grey lead-tin alloy, \
showing crossed keys within a beaded border, with a bent pin on the back and one \
lug snapped off. Soft metal, worn shallow, edges rounded by rubbing against \
cloth.

Bought in thousands at the jubilee and worn on the hat as proof of the journey.""",
  cap="A jubilee badge, worn on the hat. Proof you came, and a licence to be here."),

"14-fourteenth": dict(scene="""
A notched wooden wage tally beside a small heap of worn silver coins on a plank. \
The tally is freshly cut, pale wood showing in the notches against a darker \
weathered surface. The coins are thin, clipped and irregular.

Wages rose so fast after the plague that governments legislated to hold them \
down.""",
  cap="A fresh wage tally. After 1348 the price of a working man went up, and stayed up."),

"15-fifteenth": dict(scene="""
A guild token: a small struck brass disc with a punched symbol and a rim of \
milling, hanging from a short length of blackened cord, the brass rubbed to a \
warm shine on the high points and dark in the recesses.

Membership, which is the difference between being a workman and being a \
vagrant.""",
  cap="A guild token. The difference between a workman and a vagrant is this disc."),

"16-sixteenth": dict(scene="""
A folded parchment summons: heavy cream parchment with a formal Latin hand, \
folded twice, a red wax seal cracked across the middle where it was broken open, \
a silk cord threaded through the fold. The parchment is stained at one corner.

An instruction to appear and explain yourself.""",
  cap="A summons with a broken seal. Somebody wants you to explain yourself."),

"17-seventeenth": dict(scene="""
A health pass: a single small printed sheet with a woodcut vignette at the head, \
blanks completed in brown ink by hand, folded into a pocket-sized rectangle with \
worn creases, an applied paper seal and a stamp in dark red.

Without one of these, no gate in Italy opens for you.""",
  cap="A plague health pass, printed with the blanks filled in by hand. No gate opens without it."),

"18-eighteenth": dict(scene="""
A traveller's passport: a large single sheet of laid paper folded into eighths, \
engraved heading, long handwritten clauses in brown iron-gall ink, two red wax \
seals and a signature. Soft and furred along the folds from being carried in a \
coat.

A letter from someone important, asking that you be allowed to pass.""",
  cap="A passport, which at this date is a letter asking that you be let through."),

"19-nineteenth": dict(scene="""
A police registration card: a small stiff printed card, letterpress, with ruled \
fields completed in ink, a violet oval rubber stamp across one corner, the paper \
foxed and the edges soft.

The state has started keeping a list of who is in the city and where they \
sleep.""",
  cap="A registration card. Somebody now keeps a list of where you sleep."),

"20-twentieth": dict(scene="""
Two documents side by side: a wartime ration book, a small stapled booklet of \
perforated coupons with several already torn out, printed on cheap grey paper \
and stamped; and a folded identity card with a portrait photograph attached by \
rivets, an official stamp overlapping the photograph.

Together they decide whether you eat and whether you are stopped.""",
  cap="A ration book and an identity card. One decides if you eat, the other if you are stopped."),

}


def build(kind: str, slug: str) -> str:
  """Assemble the full prompt for one image. `kind` is scene, menu or tag."""
  if kind == "scene":
    e = SCENE[slug]
    return (f"{SCENE_STYLE}\n\nPALETTE: hold the whole image within these colours and "
        f"shades between them: {PALETTES[slug]}\n{e['scene'].strip()}\n\n"
        f"DO NOT INCLUDE ANY OF THE FOLLOWING. They did not exist at this date, or no "
        f"longer existed, and their presence is a factual error: {e['never']}.\n"
        f"Also: {NEVER}.")
  if kind == "menu":
    e = MENU[slug]
    return (f"{MENU_STYLE}\n{e['scene'].strip()}\n\n"
        f"DO NOT INCLUDE, these did not exist yet in Europe or are anachronistic here: "
        f"{e['never']}.\nAlso: {NEVER}.")
  if kind == "tag":
    e = TAG[slug]
    return (f"{TAG_STYLE}\n\nPALETTE: hold the image within these colours and shades "
        f"between them: {PALETTES[slug]}\n{e['scene'].strip()}\n\n"
        f"DO NOT INCLUDE: {TAG_NEVER}.\nAlso: {NEVER}.")
  raise ValueError(f"unknown set: {kind}")


def caption(kind: str, slug: str) -> str:
  """The page caption, rendered as HTML under the figure and never drawn into
  the image. The model renders lettering badly, and baked-in text cannot be
  selected, translated or read aloud."""
  return {"menu": MENU, "tag": TAG}[kind][slug]["cap"]
