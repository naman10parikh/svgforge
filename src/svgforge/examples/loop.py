"""Example figure: a four-step loop with one gate, drawn clockwise around its cadence."""

from svgforge import Canvas, T

STEPS = [  # clockwise from the top left
    ("Run the evals", ["Tests, lint gates and golden tasks run on a fresh machine.", "A failure is a finding too."],
     "neutral"),
    ("Find a gap", ["Compare the results with the last run.", "Look for what the rules still miss."], "neutral"),
    ("Propose a fix", ["Write the change and the evidence for it.", "Open an issue. Never merge."], "neutral"),
    ("A person reviews", ["Merges what holds up and closes what does not.", "Every change is a commit, so any step "
                          "can be undone."], "accent"),
]

ALT = (
    "A loop of four steps drawn clockwise around its cadence, every night and on every push. Run the evals: tests, "
    "lint gates and golden tasks run on a fresh machine, and a failure is a finding too. An arrow labelled results "
    "leads to Find a gap: compare the results with the last run and look for what the rules still miss. An arrow "
    "labelled a finding leads to Propose a fix: write the change and the evidence for it, open an issue, never "
    "merge. An arrow labelled a proposal leads to A person reviews, marked as the gate: they merge what holds up and "
    "close what does not, and every change is a commit, so any step can be undone. An arrow labelled merged or "
    "closed leads back to Run the evals. A bar along the bottom says the loop proposes and a person decides: it "
    "never merges by itself."
)


def loop():
    c = Canvas(1600, "An improvement loop",
               "Four steps that repeat on a schedule. The loop proposes; a person decides.",
               footer="The same shape fits any tool that carries its own evals.")
    y = c.header() + 14
    inner = c.width - 2 * c.pad
    w, gap_x, gap_y = 470, inner - 2 * 470, 150
    xl, xr = c.pad, c.pad + w + gap_x
    h = max(c.card_h(w, t, b) for t, b, _ in STEPS)
    yt, yb = y, y + h + gap_y
    spots = [(xl, yt), (xr, yt), (xr, yb), (xl, yb)]
    for (title, body, tone), (x, top) in zip(STEPS, spots):
        c.card(x, top, w, title, body, tone=tone, h=h, badge="GATE" if tone == "accent" else None)
    mid_t, mid_b = yt + h / 2, yb + h / 2
    c.arrow(xl + w + 10, mid_t, xr - 10, mid_t, T.FAINT, label="results")
    c.arrow(xr + w / 2, yt + h + 10, xr + w / 2, yb - 10, T.FAINT)
    c.text(xr + w / 2 + 12, (yt + h + yb) / 2 + 4, "a finding", 11.5, T.FAINT)
    c.arrow(xr - 10, mid_b, xl + w + 10, mid_b, T.FAINT, label="a proposal")
    c.arrow(xl + w / 2, yb - 10, xl + w / 2, yt + h + 10, T.FAINT)
    c.text(xl + w / 2 + 12, (yt + h + yb) / 2 + 4, "merged or closed", 11.5, T.FAINT)
    cx, cy = c.width / 2, (yt + h + yb) / 2
    c.text(cx, cy - 4, "every night", 24, T.TEXT, anchor="middle")
    c.text(cx, cy + 22, "and on every push", 13, T.MUTED, anchor="middle")
    bottom = c.spine(c.pad, yb + h + 36, inner, "The loop proposes. A person decides.",
                     right="it never merges by itself", color=T.MUTED)
    return c.render(c.finish(bottom), ALT), ALT


FIGURES = [{"id": "loop", "title": "An improvement loop", "build": loop}]
