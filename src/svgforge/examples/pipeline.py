"""Example figure: a left-to-right pipeline with one gate and a loop back."""

from svgforge import Canvas, T, cols, measure

STEPS = [
    ("Spec", ["A Python file describes cards, bands and arrows.", "Text widths are measured, not guessed."],
     "figures/name.py"),
    ("Render", ["svgforge build writes one SVG per figure.", "The same spec always gives the same bytes."],
     "diagrams/name.svg"),
    ("Lint", ["Fails text under 11px, text off the canvas, glyphs that render as boxes, and empty alt text."],
     "0 problems"),
    ("Look", ["Render it to PNG and read it.", "Overlaps and clipping are caught by eye."],
     "name.png, not committed"),
    ("Commit", ["The SVG, INDEX.json and the gallery go in together.", "CI runs --check, so nothing goes stale."],
     "one commit"),
]

ALT = (
    "A left-to-right pipeline of five steps for making a figure with svgforge. Spec: a Python file describes "
    "cards, bands and arrows, and text widths are measured, not guessed. Render: svgforge build writes one SVG per "
    "figure, and the same spec always gives the same bytes. Lint, marked as the gate: it fails text under 11 "
    "pixels, text outside the canvas, glyphs that render as boxes, and empty alt text. Look: the figure is rendered "
    "to PNG and read, to catch overlaps and clipping by eye. Commit: the SVG, INDEX.json and the gallery are "
    "committed together, and CI runs the build with --check so no figure goes stale. Under each step sits what it "
    "produces: figures/name.py, diagrams/name.svg, zero problems, name.png (not committed), and one commit. A "
    "curved arrow runs from Look back to Spec, labelled: fix the spec, never the SVG."
)


def pipeline():
    c = Canvas(1600, "How a figure is made",
               "Five steps from a spec to a committed SVG. Lint is the gate: a figure that fails it is never committed.",
               footer="Every step is a command an agent can run. Nothing is drawn by hand.")
    y = c.header() + 10
    inner = c.width - 2 * c.pad
    xs, w = cols(c.pad + 24, inner - 48, len(STEPS), gap=56)
    h = max(c.card_h(w, t, b) for t, b, _ in STEPS)
    c.band(c.pad, y, inner, h + 112)
    top = y + 28
    for i, (title, body, out) in enumerate(STEPS):
        gate = title == "Lint"
        c.card(xs[i], top, w, title, body, tone="accent" if gate else "neutral", h=h, badge="GATE" if gate else None)
        if i < len(STEPS) - 1:
            c.arrow(xs[i] + w + 6, top + h / 2, xs[i + 1] - 6, top + h / 2, T.FAINT)
        cw = measure(out, 11.5, True) + 22
        c.chip(xs[i] + (w - cw) / 2, top + h + 22, out, T.ACCENT if gate else T.MUTED)
    yb = y + h + 112
    x_look, x_spec = xs[3] + w / 2, xs[0] + w / 2
    dip = yb + 64
    c.path(f"M {x_look:.1f},{top + h + 58:.1f} C {x_look:.1f},{dip:.1f} {x_spec:.1f},{dip:.1f} "
           f"{x_spec:.1f},{top + h + 72:.1f}", T.ACCENT, 1.6, dash="5 5")
    c.arrow(x_spec, top + h + 74, x_spec, top + h + 58, T.ACCENT, head=7)
    c.text((x_look + x_spec) / 2, dip + 2, "fix the spec, never the SVG", 12.5, T.ACCENT, anchor="middle",
           italic=True)
    return c.render(c.finish(dip + 8), ALT), ALT


FIGURES = [{"id": "pipeline", "title": "How a figure is made", "build": pipeline}]
