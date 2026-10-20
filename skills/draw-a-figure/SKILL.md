---
name: draw-a-figure
description: Draw a new diagram as an svgforge spec, render it, lint it and look at it before committing. Use when a document needs a figure (an architecture, a pipeline, a loop, a stack, a comparison) or someone asks for a picture of a system, a flow or a structure.
---

# Draw a figure

## When to use

A document needs a diagram, or someone asks for a picture of a system, a flow or a structure.

## Steps

1. **Search first.** `svgforge find "<two or three terms>" --index diagrams/INDEX.json`, or the `svgforge_search`
   MCP tool. If the figure exists, update its spec instead of drawing a new one.
2. **Plan the reading order.** In one line each: what the eye lands on first (it gets the one accent), what comes
   second, and what is detail. List the facts that must appear.
3. **Write the spec** in `figures/<id>.py`. Start from the bundled example with the same shape: `pipeline` (left to
   right, one gate), `loop` (a cycle with a gate) or `stack` (layers with pills); `svgforge demo --out /tmp/demo`
   shows all three, and AUTHORING.md has the API. Use `cols()` or `weighted_cols()` for rows and `card_h()` to give
   a row one height. Keep card bodies to three lines or fewer.
4. **Write the alt text:** 80 to 200 words of plain prose naming every element and relation, in reading order.
5. **Build and lint:** `svgforge build figures --out diagrams`. Fix every problem it prints, in the spec.
6. **Look:** `cairosvg diagrams/<id>.svg -o /tmp/<id>.png --output-width 1600` (or any SVG-to-PNG tool), then read
   the PNG. Check for overlapping text, text escaping a card, rows out of line, arrows through boxes, and clipping.
7. **Commit** the spec, the SVG, `INDEX.json` and the gallery `README.md` together.

## Output

- `figures/<id>.py`, `diagrams/<id>.svg`, and the updated `diagrams/INDEX.json` and `diagrams/README.md`.
- One line of report: the figure id, its size in bytes, "0 lint problems", and what you checked in the PNG.

## Anti-patterns

- Writing SVG XML by hand, or editing the SVG after the build.
- Three accents in one figure: if three things carry it, none do.
- An alt text that says "a diagram of the system". Name everything.
