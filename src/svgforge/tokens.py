"""Colour tokens, tones and the glyphs that are unsafe inside a text node.

The house look: warm paper, dark ink, one accent for the single thing that matters, and one sans family.
"""

from __future__ import annotations

import math


def oklch_to_hex(L: float, C: float, h_deg: float) -> str:
    """Convert an OKLCH colour to hex. SVG 1.1 needs hex; design tokens often arrive in OKLCH."""
    h = math.radians(h_deg)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (
        4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
        -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
        -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_,
    )
    out = []
    for c in lin:
        c = max(0.0, min(1.0, c))
        c = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
        out.append(round(max(0.0, min(1.0, c)) * 255))
    return "#%02X%02X%02X" % tuple(out)


class T:
    """The tokens every figure draws with. ACCENT is the one accent; TEAL means open or shared, ROSE closed or a
    risk, VIOLET the outside world. The AMBER names are kept as aliases of ACCENT so older specs still build."""

    BG = "#fbfaf7"  # paper
    SURFACE = "#f3f0e8"  # panel band
    CARD = "#ffffff"  # card fill
    CARD_HI = "#efebe2"  # raised card
    LINE = "#e4e0d6"  # hairline
    LINE_HI = "#cdc7ba"  # visible border

    TEXT = "#1c1b18"  # ink
    MUTED = "#5f5b53"  # secondary
    FAINT = "#6f6a61"  # micro-labels, arrow glyphs (5:1 on paper)

    ACCENT = "#2f5d8a"  # the ONE accent
    ACCENT_DEEP = "#1e3f60"
    ACCENT_SOFT = "#1e3f60"  # accent text on its wash
    ACCENT_WASH = "#e4ecf4"
    AMBER, AMBER_DEEP, AMBER_SOFT, AMBER_WASH = ACCENT, ACCENT_DEEP, ACCENT_SOFT, ACCENT_WASH

    # semantic seconds, used only where meaning demands a second hue
    TEAL = "#2f6b4f"  # open / free / shared
    TEAL_WASH = "#e3efe8"
    ROSE = "#8a4b2f"  # closed / proprietary / risk
    ROSE_WASH = "#f5e9e2"
    VIOLET = "#5b4b8a"  # reserved: third party, the outside world
    VIOLET_WASH = "#ece8f5"

    SANS = "Instrument Sans,Avenir Next,Segoe UI,Helvetica Neue,Arial,sans-serif"
    SERIF = SANS  # the house look has no serif
    MONO = "SF Mono,JetBrains Mono,Menlo,Consolas,monospace"

    MIN_FONT = 11.0  # hard legibility floor


# Glyphs that fall back to tofu boxes when the viewer lacks the font (cairosvg is the strictest consumer).
# Structural arrows are DRAWN, never typed; sequences use Canvas.seq(). "·" and "—" are safe.
RISKY_GLYPHS = set("→←↑↓⇒⇐⟶⟵↔⇄▲▼◀▶●○■□▪▫✓✗✅❌🟡⚠★─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╬")


TONES = {
    "neutral": (T.CARD, T.LINE_HI, T.TEXT, T.MUTED),
    "raised": (T.CARD_HI, T.LINE_HI, T.TEXT, T.MUTED),
    "accent": (T.ACCENT_WASH, T.ACCENT, T.ACCENT_SOFT, T.MUTED),
    "amber": (T.ACCENT_WASH, T.ACCENT, T.ACCENT_SOFT, T.MUTED),  # alias of "accent"
    "teal": (T.TEAL_WASH, T.TEAL, T.TEAL, T.MUTED),
    "rose": (T.ROSE_WASH, T.ROSE, T.ROSE, T.MUTED),
    "violet": (T.VIOLET_WASH, T.VIOLET, T.VIOLET, T.MUTED),
    "ghost": ("none", T.LINE, T.MUTED, T.FAINT),
}

# Tones drawn with a heavier border, because they carry meaning.
STRONG_TONES = ("accent", "amber", "teal", "rose", "violet")
