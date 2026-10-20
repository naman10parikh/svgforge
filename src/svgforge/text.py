"""Text measurement and wrapping. SVG has no reflow, so every line break is computed here."""

from __future__ import annotations

# Helvetica advance widths in 1/1000 em for printable ASCII. Other sans fonts differ by a few percent; every
# container leaves a margin for that difference.
_W = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 191, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, "0": 556, "1": 556, "2": 556, "3": 556, "4": 556,
    "5": 556, "6": 556, "7": 556, "8": 556, "9": 556, ":": 278, ";": 278,
    "<": 584, "=": 584, ">": 584, "?": 556, "@": 1015, "A": 667, "B": 667,
    "C": 722, "D": 722, "E": 667, "F": 611, "G": 778, "H": 722, "I": 278,
    "J": 500, "K": 667, "L": 556, "M": 833, "N": 722, "O": 778, "P": 667,
    "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722, "V": 667, "W": 944,
    "X": 667, "Y": 667, "Z": 611, "[": 278, "\\": 278, "]": 278, "^": 469,
    "_": 556, "`": 333, "a": 556, "b": 556, "c": 500, "d": 556, "e": 556,
    "f": 278, "g": 556, "h": 556, "i": 222, "j": 222, "k": 500, "l": 222,
    "m": 833, "n": 556, "o": 556, "p": 556, "q": 556, "r": 333, "s": 500,
    "t": 278, "u": 556, "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "{": 334, "|": 260, "}": 334, "~": 584,
}
_WIDE = 620  # 1/1000 em for any glyph not in the table (·, —, accents)


def measure(text: str, size: float, bold: bool = False) -> float:
    """The width of `text` in pixels at `size`, from the table above."""
    em = sum(_W.get(ch, _WIDE) for ch in text) / 1000.0
    return em * size * (1.055 if bold else 1.0)


def unmeasured(text: str) -> set[str]:
    """The glyphs in `text` that the table does not know, so they are measured with the fallback width."""
    return {ch for ch in text if ch not in _W}


def wrap(text: str, size: float, max_w: float, bold: bool = False) -> list[str]:
    """Greedy wrap on measured width. A newline in `text` forces a break."""
    lines: list[str] = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = word if not cur else cur + " " + word
            if measure(trial, size, bold) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines
