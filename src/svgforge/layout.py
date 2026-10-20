"""Column helpers: split a width so a row of cards lines up without eyeballing."""

from __future__ import annotations


def cols(x: float, total_w: float, n: int, gap: float = 20.0) -> tuple[list[float], float]:
    """Evenly split a width into n columns. Returns (x positions, column width)."""
    w = (total_w - gap * (n - 1)) / n
    return [x + i * (w + gap) for i in range(n)], w


def weighted_cols(x: float, total_w: float, weights: list[float],
                  gap: float = 20.0) -> tuple[list[float], list[float]]:
    """Split a width in proportion to `weights`. Returns (x positions, widths)."""
    avail = total_w - gap * (len(weights) - 1)
    s = sum(weights)
    ws = [avail * w / s for w in weights]
    xs, cx = [], x
    for w in ws:
        xs.append(cx)
        cx += w + gap
    return xs, ws
