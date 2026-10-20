"""Dispatch: send a plain-language task to the skill and the command that does it.

Deterministic keyword routing. The best-scoring route wins; ties go to the earlier route; no match falls back to
drawing a figure, since that is the job most requests are.
"""

from __future__ import annotations

import re

ROUTES = [
    {"route": "convert", "skill": "ascii-to-figure",
     "command": "svgforge build figures --out diagrams",
     "keys": ["ascii", "text diagram", "box drawing", "boxes and arrows", "convert", "replace the diagram",
              "code block", "mermaid", "turn this"],
     "why": "An existing diagram in a document becomes a figure spec, with every label kept."},
    {"route": "review", "skill": "figure-review",
     "command": "svgforge lint <file.svg>",
     "keys": ["review", "lint", "legible", "overlap", "clipped", "critique", "looks wrong", "audit", "check the figure",
              "is it readable"],
     "why": "The lint gates plus a look at the rendered picture."},
    {"route": "find", "skill": "draw-a-figure",
     "command": "svgforge find \"<terms>\" --index diagrams/INDEX.json",
     "keys": ["find", "is there", "existing", "search", "already have", "which figure", "look up"],
     "why": "Search the store before drawing: the figure may already exist."},
    {"route": "check", "skill": "figure-review",
     "command": "svgforge build figures --out diagrams --check",
     "keys": ["stale", "out of date", "current", "in ci", "regenerate", "rebuild"],
     "why": "Fails when a committed SVG no longer matches its spec."},
    {"route": "draw", "skill": "draw-a-figure",
     "command": "svgforge build figures --out diagrams",
     "keys": ["draw", "new figure", "diagram of", "picture of", "illustrate", "visual", "figure for", "make a diagram"],
     "why": "Write a spec, build it, lint it, look at it."},
]


def route(task: str) -> dict:
    """The route for a task: {route, skill, command, why, score}."""
    text = re.sub(r"\s+", " ", task.lower())
    best, best_score = ROUTES[-1], 0
    for r in ROUTES:
        score = sum(1 for k in r["keys"] if re.search(r"\b" + re.escape(k) + r"\b", text))
        if score > best_score:
            best, best_score = r, score
    return {k: best[k] for k in ("route", "skill", "command", "why")} | {"score": best_score}
