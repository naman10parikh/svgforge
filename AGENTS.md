# AGENTS.md: how to use svgforge

svgforge draws diagrams as code. A figure is a Python spec; svgforge renders it to a self-contained SVG, the same
bytes on every run, and lint gates keep it legible. This file is the one set of instructions for every coding
agent; Claude Code and Gemini CLI read it through `CLAUDE.md` and `GEMINI.md`.

## What it does

- **Renders** a folder of figure specs into SVGs, plus an `INDEX.json` (each figure's id, title and full prose
  description) and a README gallery.
- **Lints** any SVG: text under 11px, text outside the canvas, glyphs that render as boxes, empty alt text, a
  collapsed canvas, broken XML.
- **Finds and reads** existing figures by their description, so "is there a picture of X?" needs no image.
- **Checks freshness:** `--check` fails when a committed SVG no longer matches its spec.

It calls no model and needs no key. The source is standard-library Python 3.10 or newer.

## The command line (`svgforge`)

Without a clone: `uvx --from git+https://github.com/naman10parikh/svgforge svgforge <command>`. In a clone:
`pip install -e .`, or `PYTHONPATH=src python3 -m svgforge <command>`.

| Command | What it does |
| --- | --- |
| `svgforge build [figures] [--out diagrams] [--only ID ...] [--check] [--json]` | Render every spec, lint each figure, write `INDEX.json` and `README.md`. `--check` writes nothing and exits 1 if anything is stale. |
| `svgforge lint FILE.svg ... [--json]` | Run the lint gates on any SVG files. |
| `svgforge demo [--out svgforge-demo]` | Render the three bundled example figures. |
| `svgforge find TERMS ... [--index FILE]` | Search a figure store by title and description; every term must appear. |
| `svgforge show ID [--index FILE]` | Print one figure's record, with its full description and its SVG path. |
| `svgforge route "TASK" [--json]` | Name the skill and the command for a task in plain words. |
| `svgforge runs [--last N]` | Show the run log. |
| `svgforge --help`, `svgforge --version` | Print help or the version, and nothing else. |

Exit codes: 0 success; 1 a lint problem, a stale file or a missing figure; 2 a missing folder or index. The index
defaults to `$SVGFORGE_INDEX`, else `diagrams/INDEX.json` in the current folder.

## The MCP server (`svgforge-mcp`, stdio)

Start it with `uvx --from git+https://github.com/naman10parikh/svgforge svgforge-mcp`; the root `.mcp.json` does
exactly that. Tools:

- `svgforge_list({index?, doc?})`: one line per figure: id, title, document.
- `svgforge_get({id, index?})`: the figure's record, with the full alt text and the SVG path.
- `svgforge_search({query, index?})`: id and title of each figure whose title or alt text holds every term.
- `svgforge_lint({path} or {svg})`: "OK" or the problems; `isError` is true when a gate fails.
- `svgforge_build({figures, out?, check?})`: one line per figure; it writes only into `out`, and nothing with
  `check`.

## Skills (`skills/`)

- `draw-a-figure`: a new diagram, from search to spec to a lint-clean SVG that has been looked at.
- `ascii-to-figure`: an ASCII diagram in a document becomes a figure, with every fact kept.
- `figure-review`: lint, freshness, a look at the PNG and an alt-text check, ending in a verdict table.

## Sub-agents (`.claude/agents/`)

- `figure-author`: writes or updates a spec and renders it.
- `figure-critic`: reviews rendered figures and changes nothing.

## How to draw a figure

1. Search the store first (`svgforge find`); the figure may exist.
2. Write the spec in `figures/<id>.py` (the API and the house rules are in `AUTHORING.md`; the bundled examples
   are in `src/svgforge/examples/`).
3. `svgforge build figures --out diagrams` until it prints 0 problems.
4. Render the PNG and read it.
5. Commit the spec, the SVG, `INDEX.json` and the gallery together.

## House rules (a figure that breaks one is not done)

One accent per figure; no typed arrows or box-drawing characters in text; no text under 11px; card bodies of three
lines or fewer; an alt text of 80 to 200 words naming every element and relation; nothing dropped when a figure
replaces an old diagram. Details: `AUTHORING.md`.

## What not to do

- Do not write or edit SVG XML by hand. Change the spec and rebuild. In Claude Code, a hook lints every SVG you
  write and shows you the problems.
- Do not type arrows into labels; draw them with `Canvas.arrow()` or `Canvas.seq()`.
- Do not drop a fact when converting a diagram. Put it in the figure or in the alt text.
- Do not commit a figure you have not looked at as a picture.
- Do not add external fonts, images or scripts to an SVG.
- Do not add a model call or a key. svgforge is deterministic.

## Verify a change

```bash
python3 -m unittest && python3 evals/run.py
```

Memory: `memory/MEMORY.md` (start here) and `memory/LEARNINGS.md` (rules from past mistakes); search them with
`python3 scripts/memory_search.py "<query>"`.
