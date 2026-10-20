# Svgforge: memory

The short bootstrap an agent reads first. Search everything else with
`python3 scripts/memory_search.py "<query>"` (BM25 over memory/, identity/, the skills, AUTHORING.md and AGENTS.md).

## What it is

Diagrams as code. A figure is a Python spec that exports `FIGURES`; `svgforge build` renders each one to a
self-contained SVG, lints it, and writes `INDEX.json` (id, title, full prose alt text) and a README gallery.
Agents reach it through the `svgforge` CLI, the `svgforge-mcp` server (5 tools), 3 skills and 2 sub-agents.

## Invariants (never break them)

- **Deterministic.** The same spec gives byte-identical files. The evals build three times and compare bytes.
- **Self-contained.** No external fonts, images or scripts in an SVG.
- **Legible.** No text under 11px, no text outside the canvas, no typed arrows or box-drawing characters in text,
  and an alt text on every figure.
- **Standard library only** in `src/`. The `e2b` package is optional and used only by `sandbox/`.
- **No model calls and no keys.** The judgement belongs to the agent and the reader.
- **The spec is the source.** Never hand-edit an SVG; change the spec and rebuild.

## Where things are

- Engine: `src/svgforge/canvas.py` (drawing), `tokens.py` (colours, tones, risky glyphs), `text.py` (widths,
  wrapping), `layout.py` (columns).
- Gates: `src/svgforge/lint.py` (7 rules: xml, font-floor, no-text, tofu, alt, collapsed, outside).
- Build and store: `src/svgforge/build.py`, `store.py`. Surfaces: `cli.py`, `mcp_server.py`, `route.py`.
- Run log: `src/svgforge/runlog.py`, default `~/.local/state/svgforge/runs.jsonl`; `SVGFORGE_RUNLOG=off` stops it.
- Evals: `evals/run.py`, `evals/golden.json`, `evals/fixtures/`. The loop: `evals/loop.py`, `.github/workflows/loop.yml`.

## Decisions

- Widths come from a Helvetica table (`text.py`, `_W`). An unknown glyph is measured at 620/1000 em; the loop
  proposes exact widths for glyphs the corpus uses.
- The index defaults to `diagrams/INDEX.json`, or `$SVGFORGE_INDEX`.
- `AMBER` (a token and a tone) is an alias of `ACCENT`, which is blue; older specs keep building.
- Specs load by file path under a module name made from that path, so two folders may both hold `pipeline.py`.
- Generated files print paths relative to the current folder, so they never carry the builder's home folder.

## Lessons

`memory/LEARNINGS.md` holds every correction as a rule. Read it before changing the engine or the gates.
