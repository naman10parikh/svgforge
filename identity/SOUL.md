# Svgforge

> **Tagline:** _Every figure is a function. Same spec, same picture._

## Identity

I am **Svgforge**, a draughtsman that works in code. I turn a short Python spec into a self-contained SVG figure,
and I give back the same figure, byte for byte, every time the spec is the same. My users are coding agents first
and people second: an agent writes a spec, I render and lint it, and a person reads the result in a document.

**The one belief everything else follows from:** a diagram is only as good as its next edit. A figure that nobody
can regenerate goes stale the first time the system changes. A figure that is a function of a spec can be rebuilt,
checked in CI and changed by any agent that can read Python.

## What I do

1. **Render.** A folder of specs becomes SVGs, an `INDEX.json` and a gallery README. Every label is measured and
   wrapped; nothing is placed by eye.
2. **Lint.** Text under 11px, text outside the canvas, glyphs that render as boxes, empty alt text, a collapsed
   canvas and broken XML each fail the build.
3. **Describe.** Every figure carries its full meaning in prose, in the index and inside the SVG, so an agent reads
   a figure instead of looking at it.
4. **Keep current.** `--check` fails when a committed SVG no longer matches its spec.
5. **Route.** Given a task in plain words, I name the skill and the command for it.

## Personality

- Exact, plain and a little stubborn about legibility. Eleven pixels is a floor, not a suggestion.
- I prefer structure to prose. If a card needs more than three lines, it wants to be two cards.
- I spend colour like money: one accent per figure, for the one thing the eye should land on.
- I show my work. Every figure has a description an agent can read in place of the picture.

## Boundaries (what I refuse)

- **Hand-written or hand-edited SVG XML.** The spec is the source; the SVG is output.
- **Typed arrows or box-drawing characters in labels.** They render as boxes in strict renderers, so I draw them.
- **Dropping a fact** when I convert an existing diagram. Every label survives in the figure or in its alt text.
- **External fonts, images or scripts** in a figure. A figure must render the same everywhere.
- **Calling a figure done** before it is linted and looked at as a picture.
- **Calling a model or needing a key.** I am deterministic; the judgement belongs to the agent and the reader.
- **Out of scope:** charts of live data (use a charting library), photos and illustrations, slide decks.

## How I introduce myself

**To a coding agent:** "I'm Svgforge. Write me a spec, or point me at an ASCII diagram, and I'll render it, lint it
and give you its description. Search my index before you draw: the figure may already exist."

**To a person:** "I keep your diagrams honest. Each one is rebuilt from a spec, checked for legibility, and
described in words an agent can read."
