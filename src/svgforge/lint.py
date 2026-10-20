"""The lint gates: the legibility floor, enforced mechanically on every figure.

Each problem is a string "<figure>: [<rule>] <what is wrong>". The rules:
  xml        not well-formed XML
  font-floor a font-size below T.MIN_FONT
  no-text    no <text> nodes at all
  tofu       a text node holds a glyph that renders as a box in strict renderers
  alt        an empty aria-label or <desc>
  collapsed  a canvas shorter than 120px
  outside    a text node placed outside the canvas
The text rules read svgforge's own output (x and y come first on every <text>); the others work on any SVG.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from .tokens import RISKY_GLYPHS, T

RULES = ("xml", "font-floor", "no-text", "tofu", "alt", "collapsed", "outside")


def lint(fid: str, svg: str) -> list[str]:
    """Every problem in one SVG string; an empty list means it passes."""
    problems: list[str] = []
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        return [f"{fid}: [xml] not well-formed XML: {exc}"]

    for size in re.findall(r'font-size="([\d.]+)"', svg):
        if float(size) < T.MIN_FONT:
            problems.append(f"{fid}: [font-floor] font-size {size} below the {T.MIN_FONT:g}px floor")
            break
    if "<text" not in svg:
        problems.append(f"{fid}: [no-text] no text nodes")
    for body in re.findall(r"<text[^>]*>(.*?)</text>", svg, flags=re.S):
        bad = sorted(set(body) & RISKY_GLYPHS)
        if bad:
            problems.append(f"{fid}: [tofu] text node holds {''.join(bad)!r} in {body[:48]!r}: "
                            "draw the arrow with Canvas.arrow() or use Canvas.seq()")
            break
    if 'aria-label=""' in svg or "<desc></desc>" in svg or "<desc/>" in svg:
        problems.append(f"{fid}: [alt] empty aria-label or desc")
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if m and float(m.group(2)) < 120:
        problems.append(f"{fid}: [collapsed] canvas height {m.group(2)} looks collapsed")
    if m:
        w, h = float(m.group(1)), float(m.group(2))
        for x, y in re.findall(r'<text x="([-\d.]+)" y="([-\d.]+)"', svg):
            if not (-2 <= float(x) <= w + 2) or not (-2 <= float(y) <= h + 2):
                problems.append(f"{fid}: [outside] text at ({x},{y}) outside the {w:g}x{h:g} canvas")
                break
    return problems


def rules_hit(problems: list[str]) -> list[str]:
    """The rule names in a list of problems, in order."""
    return [m.group(1) for p in problems if (m := re.search(r"\[([a-z-]+)\]", p))]
