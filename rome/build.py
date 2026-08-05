#!/usr/bin/env python3
"""
build.py: content/ (Markdown + TOML) -> assets/data.js

    rome/build.py            write assets/data.js
    rome/build.py --check    exit 1 if the file on disk is stale

WHY A BUILD AT ALL. Prose belongs in Markdown, where it can be read, diffed and
edited without counting quotes or escaping apostrophes inside a JavaScript string
literal. The site's runtime wants one flat data module. This bridges the two, and
it is the only build step the episode has.

WHAT IT EMITS. assets/data.js declares four globals, exactly as the hand-written
version did: CENTURIES, BEATS, REGIMES, SOURCES. index.html loads it as a plain
script before page.js, and scene.js reads CENTURIES off the global. Nothing here
knows what the page looks like; changing the design does not change this file.

THE SOURCE FORMAT
  content/NN.md        one century. TOML frontmatter between +++ fences carries
                       every number; `# heading` is the century's title; the
                       paragraphs after it become `body`.
  content/interludes.md   the doors, full-bleed statements and image plates that
                       sit between centuries, as ::: fenced directives. after=0
                       places one before the first century.
  content/frame.toml   the three regimes and the source list. No prose worth
                       writing in Markdown, so it is TOML the whole way down.

MARKDOWN IS DELIBERATELY A SUBSET. Four constructs, handled by `inline()`:
*italic*, **bold**, [text](url) and `code`. We write this content ourselves, so a
full CommonMark parser would be a dependency bought for constructs nobody uses.
If you find yourself wanting tables or footnotes in a century body, reach for
mistune (already installed) rather than growing the regexes here.

Read alongside: assets/data.js (the output, generated, do not hand-edit),
assets/page.js and assets/scene.js (the two consumers), ../CLAUDE.md (the series
rule that says Markdown is the source and Python does the building).
"""

import json
import pathlib
import re
import sys
import tomllib

HERE = pathlib.Path(__file__).resolve().parent
CONTENT = HERE / "content"
OUT = HERE / "assets" / "data.js"

FENCE = re.compile(r"^\+\+\+\s*$", re.M)
DIRECTIVE = re.compile(r"^:::(\w+)([^\n]*)\n(.*?)^:::\s*$", re.M | re.S)
# key=value pairs on a directive's opening line: after=3 src="img/x.webp" quiet=true
OPTION = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')


def inline(text: str) -> str:
    """The four Markdown constructs this episode's prose actually uses.

    <i>/<b> rather than <em>/<strong> because the stylesheet targets those and
    the hand-written data.js used them; keeping the output identical is what
    makes this build verifiable against the file it replaced."""
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def paragraphs(body: str) -> list[str]:
    return [inline(" ".join(p.split())) for p in body.strip().split("\n\n") if p.strip()]


def parse_century(path: pathlib.Path) -> dict:
    parts = FENCE.split(path.read_text(), maxsplit=2)
    if len(parts) != 3:
        sys.exit(f"{path.name}: expected TOML frontmatter between +++ fences")
    doc = tomllib.loads(parts[1])
    body = parts[2].strip()

    if not body.startswith("# "):
        sys.exit(f"{path.name}: body must open with '# ' and the century's title")
    title, _, rest = body[2:].partition("\n")

    missing = [k for k in ("n", "roman", "years", "regime", "pop", "free", "band") if k not in doc]
    if missing:
        sys.exit(f"{path.name}: missing required key(s): {', '.join(missing)}")

    return {
        "n": doc["n"], "roman": doc["roman"], "years": doc["years"],
        "regime": doc["regime"], "pop": doc["pop"],
        "cluster": doc.get("cluster", 0.5), "walls": doc.get("walls", "aurelian"),
        "spill": doc.get("spill", 0), "popNote": inline(doc.get("pop_note", "")),
        "free": doc["free"], "band": doc["band"],
        "title": inline(title.strip()),
        "body": paragraphs(rest),
        "danger": inline(doc.get("danger", "")),
        "ends": inline(doc.get("ends", "")),
    }


def parse_interludes(path: pathlib.Path) -> list[dict]:
    out = []
    for kind, optline, body in DIRECTIVE.findall(path.read_text()):
        opt = {k: (q or bare) for k, q, bare in OPTION.findall(optline)}
        if "after" not in opt:
            sys.exit(f"interludes.md: a :::{kind} is missing after=N")
        chunks = [c.strip() for c in body.strip().split("\n\n") if c.strip()]
        if kind == "plate":
            if len(chunks) != 2:
                sys.exit(f"interludes.md: :::plate after={opt['after']} needs a description "
                         f"paragraph and a caption paragraph, got {len(chunks)}")
            out.append({"after": int(opt["after"]), "kind": "plate", "src": opt.get("src", ""),
                        "what": inline(" ".join(chunks[0].split())),
                        "cap": inline(" ".join(chunks[1].split()))})
        elif kind == "door":
            if len(chunks) != 2:
                sys.exit(f"interludes.md: :::door after={opt['after']} needs an alt-text "
                         f"paragraph and a caption paragraph, got {len(chunks)}")
            for k in ("key", "src", "word", "ask"):
                if k not in opt:
                    sys.exit(f"interludes.md: :::door after={opt['after']} is missing {k}=")
            out.append({"after": int(opt["after"]), "kind": "door", "key": opt["key"],
                        "src": opt["src"], "word": opt["word"], "ask": opt["ask"],
                        "what": inline(" ".join(chunks[0].split())),
                        "cap": inline(" ".join(chunks[1].split()))})
        elif kind == "beat":
            head = chunks[0].lstrip("# ").strip()
            rec = {"after": int(opt["after"]), "kind": "beat", "yr": opt.get("year", ""),
                   "h": inline(head),
                   "p": inline(" ".join(" ".join(chunks[1:]).split()))}
            if opt.get("quiet") == "true":
                rec["quiet"] = True
            out.append(rec)
        else:
            sys.exit(f"interludes.md: unknown directive :::{kind}")
    return out


def js(value) -> str:
    """JSON is valid JavaScript for everything this file emits."""
    return json.dumps(value, ensure_ascii=False)


def render(centuries, beats, frame) -> str:
    regimes = [{"key": r["key"], "from": r["from"], "to": r["to"], "word": r["word"],
                "colour": r["colour"], "ask": r["ask"], "line": inline(r["line"])}
               for r in frame["regimes"]]
    sources = [[inline(s["title"]), s["url"]] for s in frame["sources"]]

    def block(name, rows):
        return f"const {name} = [\n" + "".join(f"  {js(r)},\n" for r in rows).rstrip(",\n") + "\n];\n"

    return (
        "/*\n"
        " * data.js: GENERATED by build.py from content/. Do not hand-edit.\n"
        " *\n"
        " * Edit content/NN.md, content/interludes.md or content/frame.toml and run\n"
        " * ./build.py. Four globals, read by page.js (the descent, the rail, the\n"
        " * readout, the payoff chart) and by scene.js (pop, cluster, walls, spill).\n"
        " *\n"
        " * Fields that carry the argument:\n"
        " *   pop      inhabitants as a RANGE, because Rome did not count itself\n"
        " *            before the 16th century. popNote names the dispute.\n"
        " *   free     months the traveller stays alive AND free. The run ends at\n"
        " *            death OR at ownership; early on the second comes first.\n"
        " *            999 = no foreseeable end, the rest of a normal life.\n"
        " *   cluster  0..1, how tightly the inhabited city packs into the Tiber bend.\n"
        " *   walls    which circuit exists: servian, aurelian, leonine.\n"
        " *   spill    fraction of built area outside the Aurelian circuit.\n"
        " */\n\n"
        + block("CENTURIES", centuries) + "\n"
        + block("BEATS", beats) + "\n"
        + block("REGIMES", regimes) + "\n"
        + block("SOURCES", sources)
    )


def main() -> int:
    files = sorted(CONTENT.glob("[0-9][0-9].md"))
    if not files:
        sys.exit(f"no century files in {CONTENT}")
    centuries = sorted((parse_century(f) for f in files), key=lambda c: c["n"])

    seen = [c["n"] for c in centuries]
    if seen != list(range(1, len(seen) + 1)):
        sys.exit(f"centuries must be numbered 1..N with no gaps, got {seen}")

    beats = sorted(parse_interludes(CONTENT / "interludes.md"), key=lambda b: b["after"])
    frame = tomllib.loads((CONTENT / "frame.toml").read_text())
    out = render(centuries, beats, frame)

    if "--check" in sys.argv:
        current = OUT.read_text() if OUT.exists() else ""
        if current != out:
            print(f"{OUT.relative_to(HERE)} is stale; run ./build.py", file=sys.stderr)
            return 1
        print(f"{OUT.relative_to(HERE)} is up to date")
        return 0

    OUT.write_text(out)
    print(f"{OUT.relative_to(HERE)}: {len(centuries)} centuries, {len(beats)} interludes, "
          f"{len(frame['regimes'])} regimes, {len(frame['sources'])} sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
