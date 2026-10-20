"""The Canvas: every figure is drawn through it, so every figure shares one visual language.

You describe cards, bands, arrows and sequences; the canvas measures, wraps and places them, and `render` returns a
self-contained SVG: no external fonts, no <image>, no script, so it renders the same in a browser, on GitHub, in a
notes app and in an image-reading model. Text is measured and wrapped, and never smaller than T.MIN_FONT.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from xml.sax.saxutils import escape

from .text import measure, wrap
from .tokens import STRONG_TONES, TONES, T


@dataclass
class Canvas:
    width: float
    title: str
    subtitle: str = ""
    footer: str = ""
    pad: float = 44.0
    _n: list[str] = field(default_factory=list)
    _y: float = 0.0  # running content bottom, for finish()

    # -- low-level ----------------------------------------------------------
    def raw(self, node: str) -> None:
        self._n.append(node)

    def _touch(self, y: float) -> None:
        self._y = max(self._y, y)

    def text(
        self, x: float, y: float, s: str, size: float = 13.5, fill: str = T.TEXT,
        bold: bool = False, anchor: str = "start", font: str = T.SANS,
        italic: bool = False, spacing: float | None = None, opacity: float = 1.0,
        rotate: tuple[float, float] | None = None,
    ) -> None:
        size = max(size, T.MIN_FONT)
        a = [
            f'x="{x:.1f}"', f'y="{y:.1f}"', f'font-family="{font}"',
            f'font-size="{size:g}"', f'fill="{fill}"',
        ]
        if bold:
            a.append('font-weight="700"')
        if anchor != "start":
            a.append(f'text-anchor="{anchor}"')
        if italic:
            a.append('font-style="italic"')
        if spacing:
            a.append(f'letter-spacing="{spacing:g}"')
        if opacity < 1.0:
            a.append(f'opacity="{opacity:g}"')
        if rotate:
            a.append(f'transform="rotate({rotate[0]:g} {rotate[1]:.1f} {y:.1f})"')
        self.raw(f'<text {" ".join(a)}>{escape(s)}</text>')
        self._touch(y + size * 0.3)

    def rect(
        self, x: float, y: float, w: float, h: float, fill: str = "none",
        stroke: str = "none", sw: float = 1.4, r: float = 12.0,
        dash: str = "", opacity: float = 1.0,
    ) -> None:
        a = [
            f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"',
            f'height="{h:.1f}"', f'rx="{r:g}"', f'fill="{fill}"',
        ]
        if stroke != "none":
            a += [f'stroke="{stroke}"', f'stroke-width="{sw:g}"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity < 1.0:
            a.append(f'opacity="{opacity:g}"')
        self.raw(f'<rect {" ".join(a)}/>')
        self._touch(y + h)

    def line(
        self, x1: float, y1: float, x2: float, y2: float, stroke: str = T.LINE_HI,
        sw: float = 1.4, dash: str = "", opacity: float = 1.0,
    ) -> None:
        a = [
            f'x1="{x1:.1f}"', f'y1="{y1:.1f}"', f'x2="{x2:.1f}"',
            f'y2="{y2:.1f}"', f'stroke="{stroke}"', f'stroke-width="{sw:g}"',
        ]
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity < 1.0:
            a.append(f'opacity="{opacity:g}"')
        self.raw(f'<line {" ".join(a)}/>')
        self._touch(max(y1, y2))

    def path(self, d: str, stroke: str = T.LINE_HI, sw: float = 1.4,
             fill: str = "none", dash: str = "") -> None:
        a = [f'd="{d}"', f'fill="{fill}"']
        if stroke != "none":
            a += [f'stroke="{stroke}"', f'stroke-width="{sw:g}"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        self.raw(f'<path {" ".join(a)}/>')

    # -- typography ---------------------------------------------------------
    def eyebrow(self, x: float, y: float, s: str, color: str = T.ACCENT) -> float:
        self.text(x, y, s.upper(), 11.5, color, bold=True, spacing=1.7)
        return y + 22

    def headline(self, x: float, y: float, s: str, size: float = 21,
                 color: str = T.TEXT, max_w: float | None = None) -> float:
        for ln in wrap(s, size, max_w or (self.width - 2 * self.pad)):
            self.text(x, y, ln, size, color, font=T.SERIF)
            y += size * 1.22
        return y + 4

    def note(self, x: float, y: float, s: str, max_w: float, size: float = 12.5,
             color: str = T.MUTED, italic: bool = False) -> float:
        for ln in wrap(s, size, max_w):
            self.text(x, y, ln, size, color, italic=italic)
            y += size * 1.42
        return y

    # -- components ---------------------------------------------------------
    def card_h(self, w: float, title: str | None, body: list[str],
               ts: float = 14.5, bs: float = 12.5) -> float:
        """Height a card needs. Call before drawing so rows can align."""
        h = 15.0
        if title:
            h += len(wrap(title, ts, w - 30, True)) * ts * 1.25 + 5
        for b in body:
            h += len(wrap(b, bs, w - 30)) * bs * 1.4
        return h + 13

    def card(
        self, x: float, y: float, w: float, title: str | None = None,
        body: list[str] | None = None, tone: str = "neutral",
        h: float | None = None, ts: float = 14.5, bs: float = 12.5,
        badge: str | None = None, dash: str = "",
    ) -> float:
        """Draw an auto-height card. Returns its bottom y."""
        body = body or []
        fill, stroke, tcol, bcol = TONES[tone]
        hh = h if h is not None else self.card_h(w, title, body, ts, bs)
        sw = 1.9 if tone in STRONG_TONES else 1.3
        self.rect(x, y, w, hh, fill, stroke, sw, dash=dash)
        cy = y + 15
        if title:
            for ln in wrap(title, ts, w - 30, True):
                cy += ts * 0.86
                self.text(x + 15, cy, ln, ts, tcol, bold=True)
                cy += ts * 0.39
        if title and body:
            cy += 3
        for b in body:
            for ln in wrap(b, bs, w - 30):
                cy += bs * 0.9
                self.text(x + 15, cy, ln, bs, bcol)
                cy += bs * 0.5
        if badge:
            bw = measure(badge, 10.5, True) + 16
            self.rect(x + w - bw - 12, y + 10, bw, 19, stroke, "none", r=9.5,
                      opacity=0.9)
            self.text(x + w - bw / 2 - 12, y + 23.5, badge, 10.5,
                      T.TEXT if tone in ("neutral", "raised", "ghost") else T.BG,
                      bold=True, anchor="middle", spacing=0.4)
        return y + hh

    def band(self, x: float, y: float, w: float, h: float,
             tone: str = "surface") -> None:
        fill = T.SURFACE if tone == "surface" else TONES[tone][0]
        self.rect(x, y, w, h, fill, T.LINE, 1.2, r=16)

    def chip(self, x: float, y: float, s: str, color: str = T.ACCENT,
             size: float = 11.5, wash: str | None = None) -> float:
        w = measure(s, size, True) + 22
        self.rect(x, y, w, size + 13, wash or "none", color, 1.2, r=(size + 13) / 2)
        self.text(x + w / 2, y + size + 4, s, size, color, bold=True,
                  anchor="middle")
        return x + w + 9

    def arrow(
        self, x1: float, y1: float, x2: float, y2: float, color: str = T.FAINT,
        sw: float = 1.6, label: str = "", dash: str = "", head: float = 7.0,
        label_side: str = "above", label_size: float = 11.5,
    ) -> None:
        ang = math.atan2(y2 - y1, x2 - x1)
        bx, by = x2 - head * 1.25 * math.cos(ang), y2 - head * 1.25 * math.sin(ang)
        self.line(x1, y1, bx, by, color, sw, dash)
        p = ang + math.pi / 2
        self.path(
            f"M {x2:.1f},{y2:.1f} "
            f"L {bx + head * 0.55 * math.cos(p):.1f},{by + head * 0.55 * math.sin(p):.1f} "
            f"L {bx - head * 0.55 * math.cos(p):.1f},{by - head * 0.55 * math.sin(p):.1f} Z",
            stroke="none", fill=color,
        )
        if label:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            off = -7 if label_side == "above" else label_size + 5
            self.text(mx, my + off, label, label_size, color, anchor="middle")

    def seq(self, x: float, y: float, items: list[str], size: float = 12.5,
            color: str = T.MUTED, tri: str = T.ACCENT, gap: float = 11.0,
            center: float | None = None) -> float:
        """A left-to-right sequence with DRAWN triangle separators, instead of typed arrows that turn into boxes in
        strict renderers. Pass `center` to centre the whole run on that x."""
        widths = [measure(s, size) for s in items]
        total = sum(widths) + (len(items) - 1) * (gap * 2 + 7)
        cx = center - total / 2 if center is not None else x
        for i, s in enumerate(items):
            self.text(cx, y, s, size, color)
            cx += widths[i]
            if i < len(items) - 1:
                cx += gap
                m = y - size * 0.30
                self.path(
                    f"M {cx:.1f},{m - 4.2:.1f} L {cx + 6.4:.1f},{m:.1f} "
                    f"L {cx:.1f},{m + 4.2:.1f} Z", stroke="none", fill=tri)
                cx += 7 + gap
        return cx

    # -- connective tissue ----------------------------------------------------
    def curve(self, x1: float, y1: float, x2: float, y2: float,
              color: str = T.LINE_HI, sw: float = 1.5, vertical: bool = True,
              dash: str = "", head: float = 0.0, opacity: float = 1.0) -> None:
        """A smooth S-bezier between two points. `vertical=True` bends through the midpoint in y (top-to-bottom
        fans); False bends through the midpoint in x (left-to-right arcs)."""
        if vertical:
            m = (y1 + y2) / 2
            d = f"M {x1:.1f},{y1:.1f} C {x1:.1f},{m:.1f} {x2:.1f},{m:.1f} {x2:.1f},{y2:.1f}"
        else:
            m = (x1 + x2) / 2
            d = f"M {x1:.1f},{y1:.1f} C {m:.1f},{y1:.1f} {m:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
        a = [f'd="{d}"', 'fill="none"', f'stroke="{color}"', f'stroke-width="{sw:g}"',
             'stroke-linecap="round"']
        if dash:
            a.append(f'stroke-dasharray="{dash}"')
        if opacity < 1.0:
            a.append(f'opacity="{opacity:g}"')
        self.raw(f'<path {" ".join(a)}/>')
        if head:
            ang = math.pi / 2 if vertical else 0.0
            p = ang + math.pi / 2
            bx, by = x2 - head * math.cos(ang), y2 - head * math.sin(ang)
            self.path(
                f"M {x2:.1f},{y2:.1f} "
                f"L {bx + head * 0.5 * math.cos(p):.1f},{by + head * 0.5 * math.sin(p):.1f} "
                f"L {bx - head * 0.5 * math.cos(p):.1f},{by - head * 0.5 * math.sin(p):.1f} Z",
                stroke="none", fill=color)
        self._touch(max(y1, y2))

    def fan(self, ox: float, oy: float, targets: list[float], ty: float,
            color: str = T.LINE_HI, sw: float = 1.4, highlight: int | None = None,
            hi_color: str = T.ACCENT, head: float = 6.0) -> None:
        """One node branching into many. `highlight` draws one branch heavier in `hi_color`."""
        for i, tx in enumerate(targets):
            hi = i == highlight
            self.curve(ox, oy, tx, ty, hi_color if hi else color,
                       sw + 1.1 if hi else sw, vertical=True, head=head,
                       opacity=1.0 if hi else 0.75)

    def accent_card(
        self, x: float, y: float, w: float, title: str, accent: str,
        lead: str = "", pills: list[str] | None = None, note: str = "",
        badge: str = "", fill: str = T.CARD, pill_tone: str | None = None,
        ts: float = 16.0,
    ) -> float:
        """A layer band: thick left accent bar, title, one lead line, a row of pills, and a muted footnote."""
        pills = pills or []
        inner = w - 34 - 22
        h = 20.0
        h += ts * 1.2
        if lead:
            h += len(wrap(lead, 13, inner)) * 13 * 1.42 + 5
        rows = self._pill_rows(pills, inner, 11.5)
        if rows:
            h += 9 + rows * 30
        if note:
            h += len(wrap(note, 11.5, inner)) * 11.5 * 1.4 + 7
        h += 15

        self.rect(x, y, w, h, fill, T.LINE, 1.1, r=12)
        self.path(f"M {x + 5:.1f},{y + 2:.1f} L {x + 5:.1f},{y + h - 2:.1f}",
                  accent, 5.5)
        cx, cy = x + 26, y + 20
        cy += ts * 0.86
        self.text(cx, cy, title, ts, accent, bold=True)
        cy += ts * 0.34
        if lead:
            cy = self.note(cx, cy + 16, lead, inner, 13, T.TEXT) + 1
        if rows:
            cy = self.pills(cx, cy + 10, inner, pills,
                            pill_tone or accent, 11.5) + 2
        if note:
            cy = self.note(cx, cy + 15, note, inner, 11.5, T.FAINT, italic=True)
        if badge:
            bw = measure(badge, 10.5, True) + 20
            self.rect(x + w - bw - 14, y + 13, bw, 20, "none", accent, 1.2, r=10)
            self.text(x + w - bw / 2 - 14, y + 27, badge, 10.5, accent, bold=True,
                      anchor="middle", spacing=0.4)
        self._touch(y + h)
        return y + h

    def _pill_rows(self, items: list[str], max_w: float, size: float) -> int:
        if not items:
            return 0
        rows, cx = 1, 0.0
        for s in items:
            w = measure(s, size, True) + 24
            if cx + w > max_w and cx:
                rows += 1
                cx = 0.0
            cx += w + 8
        return rows

    def pills(self, x: float, y: float, max_w: float, items: list[str],
              color: str = T.ACCENT, size: float = 11.5,
              wash: str | None = None) -> float:
        """An auto-wrapping row of chips. Returns the bottom y."""
        cx, cy = x, y
        for s in items:
            w = measure(s, size, True) + 24
            if cx + w > x + max_w and cx > x:
                cx, cy = x, cy + 30
            self.rect(cx, cy, w, size + 13, wash or "none", color, 1.1,
                      r=(size + 13) / 2)
            self.text(cx + w / 2, cy + size + 4, s, size, color, anchor="middle")
            cx += w + 8
        return cy + size + 13

    def bracket(self, x: float, y1: float, y2: float, label: str,
                color: str = T.MUTED, side: str = "right",
                sub: str = "") -> None:
        """A grouping bracket spanning rows: these belong together."""
        d = 12 if side == "right" else -12
        self.path(f"M {x:.1f},{y1:.1f} L {x + d:.1f},{y1:.1f} "
                  f"L {x + d:.1f},{y2:.1f} L {x:.1f},{y2:.1f}", color, 1.4)
        tx = x + d + (12 if side == "right" else -12)
        anchor = "start" if side == "right" else "end"
        my = (y1 + y2) / 2
        lines = sub.split("\n") if sub else []
        ty = my - (2 + 7 * (len(lines) - 1) if lines else -4)
        self.text(tx, ty, label, 11.5, color, bold=True, anchor=anchor, spacing=0.8)
        for i, ln in enumerate(lines):  # SVG text has no newline: one node per line
            self.text(tx, ty + 16 + i * 14, ln, 11, T.FAINT, anchor=anchor)

    def spine(self, x: float, y: float, w: float, label: str, right: str = "",
              color: str = T.ACCENT, h: float = 46.0) -> float:
        """The shared bar everything above rides on."""
        self.rect(x, y, w, h, T.ACCENT_WASH if color == T.ACCENT else "none",
                  color, 2.0, r=10)
        self.text(x + 22, y + h / 2 + 5, label, 14, color, bold=True)
        if right:
            self.text(x + w - 22, y + h / 2 + 5, right, 12, T.MUTED, anchor="end")
        return y + h

    def legend(self, x: float, y: float, items: list[tuple[str, str]],
               size: float = 11.5) -> float:
        cx = x
        for label, color in items:
            self.rect(cx, y - size + 2, 11, 11, color, "none", r=3)
            self.text(cx + 17, y, label, size, T.MUTED)
            cx += 17 + measure(label, size) + 24
        return y + 18

    def rule(self, y: float, color: str = T.LINE) -> float:
        self.line(self.pad, y, self.width - self.pad, y, color, 1.0)
        return y + 1

    # -- assembly -----------------------------------------------------------
    def header(self) -> float:
        """Title, subtitle and the accent rule. Returns the y where content starts."""
        y = self.pad + 30
        self.text(self.pad, y, self.title, 30, T.TEXT, font=T.SERIF)
        y += 12
        if self.subtitle:
            y = self.note(self.pad, y + 14, self.subtitle,
                          self.width - 2 * self.pad - 40, 14, T.MUTED) + 6
        self.line(self.pad, y + 4, self.pad + 54, y + 4, T.ACCENT, 2.6)
        return y + 30

    def finish(self, y: float) -> float:
        """Draw the footer caption and return the final canvas height."""
        y = max(y, self._y) + 30
        if self.footer:
            y = self.note(self.pad, y + 6, self.footer,
                          self.width - 2 * self.pad, 12.5, T.FAINT, italic=True)
        return y + self.pad - 6

    def render(self, height: float, alt: str) -> str:
        """The SVG string. `alt` becomes the aria-label and the <desc>: what an agent reads instead of the picture."""
        h = round(height)
        body = "".join(self._n)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width:g}" '
            f'height="{h}" viewBox="0 0 {self.width:g} {h}" '
            f'preserveAspectRatio="xMidYMid meet" role="img" '
            # attribute context: saxutils.escape leaves " alone, which would end the attribute early
            f'aria-label="{escape(alt, {chr(34): "&quot;"})}">'
            f"<title>{escape(self.title)}</title>"
            f"<desc>{escape(alt)}</desc>"
            f'<rect x="0" y="0" width="{self.width:g}" height="{h}" '
            f'fill="{T.BG}"/>{body}</svg>\n'
        )
