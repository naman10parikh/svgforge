---
name: figure-review
description: Review rendered figures for legibility and honesty, by running the lint gates and the freshness check and by looking at each picture against the house rules. Use before merging a change that touches a figure, when a figure looks off, or to audit a folder of diagrams.
---

# Review a figure

## When to use

Before merging any change to a spec or an SVG, when someone says a figure looks wrong, or when auditing a folder of
diagrams.

## Steps

1. **Lint:** `svgforge lint diagrams/*.svg`, or the `svgforge_lint` MCP tool. Every problem blocks the merge.
2. **Freshness:** `svgforge build figures --out diagrams --check`. A stale file means the SVG and its spec
   disagree: rebuild it; never hand-edit it.
3. **Look:** render each changed figure to PNG and read it. Check for text overlapping text, text escaping its
   card, rows out of line, arrows passing through boxes, and anything clipped at the edge.
4. **House rules:** one accent only, no typed arrows, card bodies of three lines or fewer, labels of 11px or more,
   light paper and dark ink.
5. **Alt text:** read it with `svgforge show <id>`. It must name every element and relation in the picture, in 80
   to 200 words, and say nothing the picture does not show.
6. **Verdict:** pass, or a numbered list of fixes, each naming the figure id and the spec line to change.

## Output

A table with one row per figure: id · lint (pass, or the rules hit) · current (yes or stale) · look (pass, or what
is wrong) · alt (pass, or what is missing) · verdict. Then the numbered fixes.

## Anti-patterns

- Passing a figure on lint alone: the lint cannot see an overlap.
- Fixing the SVG instead of the spec.
