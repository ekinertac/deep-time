#!/usr/bin/env python3
"""
build.py: turn content/*.md into pages/*.html and assets/data.js.

WHY THIS EXISTS. Episode 01 was twenty thousand words hand-written directly into
sixteen HTML files, and every editing pass after that was string-matching prose
against markup. A single reflow of indentation broke every patch. Here the prose
lives in markdown, the markup lives in one template, and this script is the only
thing that knows how to join them. Editing a sentence means editing a sentence.

    ./build.py            rebuild everything
    ./build.py 03 07      rebuild two centuries
    ./build.py --check    parse and validate, write nothing

NO DEPENDENCIES, on purpose, matching the rest of the repo. TOML front matter is
read by stdlib tomllib. The markdown is deliberately a small subset, handled by
`inline()` below: paragraphs, *emphasis*, **strong**, [links](url) and nothing
else. If a page ever needs more than that, the honest fix is to ask whether the
page needs it, not to add a markdown library.

SINGLE SOURCE OF TRUTH. Figure captions are NOT in the markdown: they come from
prompts.py, because that is where the image they caption is specified, and a
caption that drifts from its prompt is how episode 01 ended up describing
pictures it no longer had. Alt text IS in the markdown, because it has to be
written while looking at the finished image, which does not exist yet when the
prompt is written.

Read alongside: templates/page.html (the markup), content/*.md (the prose),
prompts.py (image prompts and captions), ../tools/gen_img.py (makes the images).
"""

import html
import pathlib
import re
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE / "content"
PAGES = HERE / "pages"
TEMPLATE = HERE / "templates" / "page.html"

sys.path.insert(0, str(HERE))
import prompts  # noqa: E402  (needs HERE on the path first)


# ---------------------------------------------------------------------------
# The markdown subset
# ---------------------------------------------------------------------------

def inline(text: str) -> str:
    """Escape HTML, then re-introduce the four inline forms we actually use.

    Order matters: escaping first means a stray < in the prose cannot become a
    tag, and the markers we then convert are ones the escape pass leaves alone.
    """
    t = html.escape(text.strip(), quote=False)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def paragraphs(text: str, indent: str = "    ") -> str:
    """Blank-line separated blocks become <p>. Single newlines are just wrapping
    in the source file and carry no meaning."""
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        if block.strip():
            out.append(f"{indent}<p>{inline(' '.join(block.split()))}</p>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# The file format
# ---------------------------------------------------------------------------

def parse(path: pathlib.Path) -> dict:
    """Split a content file into front matter and `##` sections, each of which
    may hold an intro paragraph and a run of `###` items.

    An item heading starting with `!` marks the emphatic variant: the fatal beat
    on the timeline, the missing resource in the kit. One convention, two uses,
    so there is nothing to remember.
    """
    raw = path.read_text()
    if not raw.startswith("+++"):
        sys.exit(f"{path.name}: must start with a +++ TOML front matter block")
    _, fm, body = raw.split("+++", 2)
    doc = tomllib.loads(fm)

    doc["sections"] = {}
    for chunk in re.split(r"^## ", body, flags=re.M)[1:]:
        head, _, rest = chunk.partition("\n")
        parts = re.split(r"^### ", rest, flags=re.M)
        section = {"intro": parts[0].strip(), "items": []}
        for item in parts[1:]:
            title, _, text = item.partition("\n")
            title = title.strip()
            flag = title.startswith("!")
            title = title.lstrip("!").strip()
            label, sep, name = title.partition("|")
            section["items"].append({
                "label": label.strip() if sep else "",
                "title": (name if sep else label).strip(),
                "body": text.strip(),
                "flag": flag,
            })
        doc["sections"][head.strip().lower()] = section
    return doc


def need(doc: dict, path: pathlib.Path, *keys: str) -> None:
    missing = [k for k in keys if k not in doc]
    if missing:
        sys.exit(f"{path.name}: front matter is missing {', '.join(missing)}")


# ---------------------------------------------------------------------------
# Rendering the repeated blocks. The template holds the page skeleton and
# nothing that repeats, so there is no loop syntax to invent or debug.
# ---------------------------------------------------------------------------

def dateline(parts) -> str:
    """The hero's second line is two or three separate facts, not one string with
    markup in it. Content files stay free of HTML entities; the separator is
    build.py's business."""
    if isinstance(parts, str):
        parts = [parts]
    return "&nbsp;&middot;&nbsp;".join(inline(p) for p in parts)


def render_vitals(doc: dict) -> str:
    """Two numbers per meter, not one. `pct` is this century's value on the
    stated scale and `now` is today's value on the same scale, drawn as a tick.
    A bar with nothing to compare against says very little, and the whole point
    of the row is the distance between the fill and the tick."""
    rows = []
    for v in doc.get("vitals", []):
        cls = "vital vital--danger" if v.get("danger") else "vital"
        unit = f"<small>{inline(v['unit'])}</small>" if v.get("unit") else ""
        rows.append(f"""   <div class="{cls}">
    <span class="vital__k">{inline(v['k'])}</span>
    <span class="vital__v">{inline(v['v'])}{unit}</span>
    <div class="meter" style="--pct:{v['pct']}; --now:{v['now']}"><div class="meter__fill"></div><div class="meter__now"></div></div>
    <p class="vital__note">{inline(v.get('note', ''))}</p>
   </div>""")
    return "\n".join(rows)


def render_beats(section: dict) -> str:
    out = []
    for b in section["items"]:
        cls = "beat beat--fatal" if b["flag"] else "beat"
        out.append(f"""   <div class="{cls}">
    <span class="beat__t">{inline(b['label'])}</span>
    <h3 class="beat__h">{inline(b['title'])}</h3>
{paragraphs(b['body'], '    ')}
   </div>""")
    return "\n".join(out)


def render_kit(section: dict) -> str:
    out = []
    for k in section["items"]:
        cls = "kit__item kit__item--none" if k["flag"] else "kit__item"
        out.append(f"""   <div class="{cls}"><h3>{inline(k['title'])}</h3>"""
                   f"""<p>{inline(' '.join(k['body'].split()))}</p></div>""")
    return "\n".join(out)


def render_caveats(section: dict) -> str:
    out = []
    for c in section["items"]:
        out.append(f"""  <div class="caveat">
   <strong>{inline(c['title'])}</strong> {inline(' '.join(c['body'].split()))}
  </div>""")
    return "\n".join(out)


def figure(doc: dict, kind: str, cls: str, ratio: tuple[int, int]) -> str:
    """Captions come from prompts.py; alt comes from the markdown."""
    folder = prompts.SETS[kind][0]
    alt = doc.get("alt", {}).get(kind, "")
    cap = prompts.caption(kind, doc["slug"]) if kind != "scene" else doc.get("scene_caption", "")
    capcls = ' class="scene__cap"' if kind == "scene" else ""
    w, h = ratio
    return (f"""<figure class="{cls}">
    <img src="../assets/scenes/{folder}/{doc['slug']}.webp" width="{w}" height="{h}"
       alt="{html.escape(alt)}" loading="lazy">
    <figcaption{capcls}>{inline(cap)}</figcaption>
   </figure>""")


def render(doc: dict, template: str) -> str:
    s = doc["sections"]
    fields = {
        "slug": doc["slug"],
        "n": f"{doc['n']:02d}",
        "total": str(len(prompts.SLUGS)),
        "name": inline(doc["name"]),
        "eyebrow": inline(doc.get("eyebrow", "")),
        "dates": dateline(doc["dates"]),
        "title": html.escape(doc.get("title", f"{doc['name']}: how long would you last?")),
        "description": html.escape(doc.get("description", "")),
        "lede": paragraphs(s["lede"]["intro"], "   "),
        "verdict": inline(doc["verdict"]),
        "verdict_note": paragraphs(doc.get("verdict_note", ""), "    "),
        "hero_figure": figure(doc, "scene", "scene", (1792, 768)),
        "vitals": render_vitals(doc),
        "clock_intro": inline(s["clock"]["intro"]),
        "beats": render_beats(s["clock"]),
        "tag_figure": figure(doc, "tag", "split__fig", (1264, 848)),
        "survive_intro": inline(s["survive"]["intro"]),
        "menu_figure": figure(doc, "menu", "split__fig", (1264, 848)),
        "kit": render_kit(s["survive"]),
        "caveats": render_caveats(s["doubt"]),
    }
    missing = set(re.findall(r"\{\{(\w+)\}\}", template)) - set(fields)
    if missing:
        sys.exit(f"template wants fields that build.py does not supply: {sorted(missing)}")
    for k, v in fields.items():
        template = template.replace("{{" + k + "}}", v)
    return template


# ---------------------------------------------------------------------------
# data.js, so the rail, the pagers and the index all read one generated list
# rather than a hand-maintained copy of the same twenty facts.
# ---------------------------------------------------------------------------

def render_data(docs: list[dict]) -> str:
    rows = []
    for d in docs:
        rows.append("  {{ n: {n}, slug: {slug!r}, name: {name!r}, dates: {dates!r}, "
                    "verdict: {verdict!r}, band: {band!r} }},".format(
                        n=d["n"], slug=d["slug"], name=d["name"],
                        dates=d["dates"][0] if isinstance(d["dates"], list) else d["dates"],
                        verdict=d["verdict"], band=d.get("band", "")).replace("'", '"'))
    return ("/* GENERATED by build.py from content/*.md. Do not edit. */\n"
            "const CENTURIES = [\n" + "\n".join(rows) + "\n];\n\n"
            "const pageFile = c => `pages/${c.slug}.html`;\n")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    check = "--check" in sys.argv
    files = sorted(CONTENT.glob("*.md"))
    if not files:
        sys.exit(f"no content in {CONTENT}")
    docs = []
    for f in files:
        doc = parse(f)
        need(doc, f, "n", "slug", "name", "dates", "verdict")
        if doc["slug"] not in prompts.SLUGS:
            sys.exit(f"{f.name}: slug {doc['slug']!r} is not in prompts.SLUGS")
        docs.append(doc)
    docs.sort(key=lambda d: d["n"])

    template = TEMPLATE.read_text()
    PAGES.mkdir(exist_ok=True)
    written = 0
    for doc in docs:
        if args and not any(a.lstrip("0") == str(doc["n"]) for a in args):
            continue
        out = render(doc, template)
        if not check:
            (PAGES / f"{doc['slug']}.html").write_text(out)
        written += 1
    if not check:
        (HERE / "assets" / "data.js").write_text(render_data(docs))
    print(f"  {written} page(s) {'checked' if check else 'written'}, "
          f"{len(docs)} in data.js")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
