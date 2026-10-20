---
name: ascii-to-figure
description: Replace an ASCII or box-drawing diagram in a Markdown document with an svgforge figure, keeping every label, number and relation. Use when a document holds a diagram drawn with characters in a code block (boxes, arrows, trees, tables) that should become a real figure.
---

# Turn an ASCII diagram into a figure

## When to use

A Markdown file has a diagram drawn with characters inside a code fence, and it should read as a figure on GitHub
and in an agent's context.

## Steps

1. **List the facts.** Write down every label, number, name and arrow in the block. This list is the acceptance
   test: each item must appear in the figure or in its alt text.
2. **Pick the shape.** Steps from left to right: a pipeline. A cycle: a loop. Layers: a stack. A tree: `fan()`.
   Groups: `bracket()`.
3. **Write the spec** in `figures/<id>.py`, as in the draw-a-figure skill, steps 3 and 4. Set `doc` to the Markdown
   file's path and `anchor` to the heading the block sits under.
4. **Build, lint, look:** `svgforge build figures --out diagrams`, then render the PNG and read it.
5. **Check the list.** Tick each fact against the figure and the alt text; put back anything missing.
6. **Place the figure above the block:** `![<first sentence of the alt text>](diagrams/<id>.svg)`. Keep the original
   ASCII below it inside a collapsed `<details>` block, so nothing is lost and it stays searchable.

## Output

- The spec and the rendered figure.
- The document, with the image above a collapsed copy of the original block.
- The fact list, every item ticked.

## Anti-patterns

- Deleting the ASCII block. Collapse it; never remove it.
- Rewriting the document's prose. Place the figure and leave the words alone.
- Merging two facts into one label to save room. Split the card instead.
