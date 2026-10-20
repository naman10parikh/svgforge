"""Example figure: a layered stack of bands with pills, a grouping bracket and a spine."""

from svgforge import Canvas, T

LAYERS = [
    ("Surfaces", "How people and agents reach it.",
     ["command line", "MCP server", "skills", "plugin", "agent card"], ""),
    ("Engine", "The deterministic core: the same input always gives the same output.",
     ["measure", "wrap", "place", "render"], ""),
    ("Gates", "Checks that stop a bad result before anyone relies on it.",
     ["lint", "unit tests", "golden tasks", "stale check"], "NOTHING SHIPS WITHOUT THEM"),
    ("Memory", "What it has learned, kept as rules it can search.",
     ["MEMORY.md", "LEARNINGS.md", "BM25 search"], ""),
    ("Runtime", "Where it runs, away from your own machine.",
     ["CI runner", "E2B sandbox", "run log"], ""),
]

ALT = (
    "A stack of five layers that make up a self-improving tool, read from top to bottom, resting on Git. "
    "Surfaces: how people and agents reach it, through the command line, an MCP server, skills, a plugin and an "
    "agent card. Engine: the deterministic core, where the same input always gives the same output: measure, "
    "wrap, place, render. Gates, the highlighted layer, marked nothing ships without them: checks that stop a bad "
    "result before anyone relies on it, namely lint, unit tests, golden tasks and a stale check. Memory: what it "
    "has learned, kept as rules it can search, in MEMORY.md, LEARNINGS.md and a BM25 search. Runtime: where it "
    "runs, away from your own machine, on a CI runner or an E2B sandbox, with a run log. A bracket on the right "
    "groups all five layers as one repository, versioned together. The base bar reads Git: every change is a "
    "commit you can revert."
)


def stack():
    c = Canvas(1600, "A self-improving tool, layer by layer",
               "Five layers in one repository. The gates are what make the rest safe to change.",
               footer="Read it top down: what you call, what computes, what checks, what remembers, where it runs.")
    y = c.header() + 6
    inner = c.width - 2 * c.pad
    w = inner - 210
    top = y
    for title, lead, pills, badge in LAYERS:
        hi = title == "Gates"
        y = c.accent_card(c.pad, y, w, title, T.ACCENT if hi else T.TEXT, lead=lead, pills=pills, badge=badge,
                          fill=T.ACCENT_WASH if hi else T.CARD, pill_tone=None if hi else T.MUTED) + 14
    c.bracket(c.pad + w + 16, top + 4, y - 18, "ONE REPOSITORY", sub="versioned\ntogether")
    bottom = c.spine(c.pad, y + 8, inner, "Git", right="every change is a commit you can revert",
                    color=T.MUTED)
    return c.render(c.finish(bottom), ALT), ALT


FIGURES = [{"id": "stack", "title": "A self-improving tool, layer by layer", "build": stack}]
