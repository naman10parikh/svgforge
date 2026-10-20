# Authoring a figure with svgforge

A figure is a Python spec that svgforge renders. You never hand-write SVG XML, and you never judge a text width
by eye. You describe cards, bands, arrows and sequences; the engine measures, wraps and places them.

## The loop

```bash
svgforge build figures --out diagrams                                # render every spec and lint each figure
cairosvg diagrams/<id>.svg -o /tmp/<id>.png --output-width 1600      # or any SVG-to-PNG tool
# then read the PNG as an image and fix what looks wrong. This step is not optional.
```

`svgforge build` fails on text under 11px, text outside the canvas, empty alt text, a glyph that renders as a box,
a collapsed canvas and broken XML. `svgforge build --check` writes nothing and fails when a committed SVG no
longer matches its spec, which is what CI should run.

## A spec

A spec is any `.py` file in your figures folder. Files whose names start with `_` are helpers that specs may
import; they are not loaded as specs. A spec exports `FIGURES`:

```python
from svgforge import Canvas, T, cols, measure

def my_figure():
    c = Canvas(1600, "Board title", "One or two sentences of subtitle.",
               footer="Optional italic caption at the bottom.")
    y = c.header()
    ...
    y = c.finish(y)          # draws the footer and returns the final height
    alt = "Full prose narration of the whole figure. This is what an agent reads."
    return c.render(y, alt), alt

FIGURES = [
    {"id": "my-figure", "title": "Board title", "build": my_figure,
     "doc": "docs/guide.md", "anchor": "The heading it sits under"},   # doc and anchor are optional
]
```

Three working specs ship inside the package, in `src/svgforge/examples/`: a pipeline, a loop and a layered stack.
`svgforge demo --out /tmp/demo` renders them. Copy the one closest to your shape.

## The API

**Canvas**: `Canvas(width, title, subtitle="", footer="", pad=44)`

| Call                    | Does                                                               |
| ----------------------- | ------------------------------------------------------------------ |
| `c.header()`            | title, subtitle and the accent rule. Returns the y to start at.    |
| `c.finish(y)`           | the footer caption. Returns the final height for `render`.         |
| `c.render(height, alt)` | the SVG string. `alt` becomes the `aria-label` and the `<desc>`.   |
| `c.pad` / `c.width`     | margins. The usable width is `c.width - 2 * c.pad`.                |

**Cards**: the workhorse. Height is computed from the content.

```python
h = c.card_h(w, title, body_lines)              # measure first, so a row can align
bottom = c.card(x, y, w, title, body_lines,     # body_lines is a list[str]
                tone="neutral", h=h,            # pass h to give a row one height
                ts=14.5, bs=12.5,               # title and body font sizes
                badge="GATE", dash="4 5")       # optional pill and dashed border
```

Tones: `neutral` (default) · `raised` (one step darker) · `accent` (the one emphasis: use it for the thing the eye
should land on) · `teal` (open, free, shared) · `rose` (closed, proprietary, a risk) · `violet` (a third party, the
outside world) · `ghost` (outline only). `amber` is an older name for `accent`.

**Layout**

```python
xs, w  = cols(x, total_w, n, gap=20)                   # n equal columns
xs, ws = weighted_cols(x, total_w, [2, 1, 1], gap=20)  # proportional columns
```

Uniform rows: compute `h = max(c.card_h(w, t, b) for t, b in items)`, then pass `h=h` to every card in the row.
Never eyeball a height.

**Other primitives**

```python
c.eyebrow(x, y, "SECTION LABEL")                  # small capitals in the accent colour
c.headline(x, y, "Headline", size=21)             # wraps; returns the next y
c.note(x, y, "prose", max_w, size=12.5)           # wraps; returns the next y
c.chip(x, y, "LABEL", color=T.TEAL)               # returns the next x
c.band(x, y, w, h)                                # a recessed surface panel
c.rect(x, y, w, h, fill, stroke, sw, r, dash)
c.line(x1, y1, x2, y2, stroke, sw, dash)
c.arrow(x1, y1, x2, y2, color, sw, label="")      # a line with a drawn triangle head
c.seq(x, y, ["a", "b", "c"], center=c.width / 2)  # a sequence with drawn separators
c.curve(x1, y1, x2, y2, color, vertical=True)     # an S-curve connector
c.fan(ox, oy, [x1, x2, x3], ty, highlight=1)      # one node branching into many
c.accent_card(x, y, w, title, accent, lead, pills, note, badge)   # a layer band with pills
c.pills(x, y, max_w, ["a", "b"])                  # a wrapping row of chips
c.bracket(x, y1, y2, "LABEL", sub="two\nlines")   # groups rows
c.spine(x, y, w, "Base", right="note")            # the bar everything rests on
c.legend(x, y, [("label", T.ACCENT), ...])
c.rule(y)                                         # a hairline across the board
c.text(x, y, s, size, fill, bold, anchor, font, italic, spacing, rotate)
c.path(d, stroke, sw, fill, dash)                 # curves and custom shapes
```

Tokens live on `T`: `T.BG`, `T.SURFACE`, `T.CARD`, `T.LINE`, `T.TEXT`, `T.MUTED`, `T.FAINT`, `T.ACCENT` (with
`ACCENT_WASH`, `ACCENT_SOFT`, `ACCENT_DEEP`), `T.TEAL`, `T.ROSE`, `T.VIOLET` and their washes, `T.SANS`, `T.MONO`
and `T.MIN_FONT`. `oklch_to_hex(L, C, h)` converts an OKLCH colour for a custom token.

## House rules (the build fails, or the reviewer rejects)

1. **Light paper, one accent.** Warm paper `T.BG`, dark ink, one sans family. The accent marks the single thing
   that matters most. If three things carry it, none do.
2. **No typed arrows.** `→ ← ↑ ↓ ✅ ❌ ─ │ ┌` and their kind render as boxes in strict renderers. Use `c.arrow()`
   for structure and `c.seq()` for inline sequences; `·` and `—` are fine in prose.
3. **11px floor.** Captions 11.5 to 12.5, body 12.5 to 13.5, card titles 13.5 to 15, headlines 18 to 22, the
   board title 30.
4. **Zero detail loss.** When a figure replaces an existing diagram, every label, number, name and distinction
   survives in the figure or in its alt text. Make it less wordy; never drop a fact.
5. **Less text, more structure.** A card body past three lines wants to be two cards, a row of chips or a table.
6. **The alt text is a deliverable.** It is what an agent reads instead of the picture, and the accessibility
   surface. Narrate the whole figure in plain prose, naming every element and relation: 80 to 200 words.
7. **Read the PNG before you call it done.** Valid XML is not legible. Look for overlapping text, text escaping a
   card, rows that do not line up, arrows through boxes, and anything clipped at the edge.

## Width and height

The default width is 1600. The height is whatever `finish()` returns; tall boards are fine. Keep 1600 unless the
content needs another shape.
