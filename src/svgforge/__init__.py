"""svgforge: diagrams as code. A figure is a Python spec; the engine measures, wraps and places every label and
writes a self-contained SVG, byte for byte the same on every run. Lint gates keep every figure legible.

    from svgforge import Canvas, T, cols

Authoring guide: AUTHORING.md in the repository.
"""

from __future__ import annotations

from .canvas import Canvas
from .layout import cols, weighted_cols
from .lint import lint
from .text import measure, unmeasured, wrap
from .tokens import RISKY_GLYPHS, TONES, T, oklch_to_hex

__version__ = "0.1.0"

__all__ = ["Canvas", "T", "TONES", "RISKY_GLYPHS", "cols", "weighted_cols", "measure", "wrap", "unmeasured",
           "lint", "oklch_to_hex", "__version__"]
