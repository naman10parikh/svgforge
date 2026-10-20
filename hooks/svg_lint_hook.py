#!/usr/bin/env python3
"""A Claude Code PostToolUse hook: after a Write or an Edit to an .svg file, run svgforge's lint gates on it.

A failing figure exits 2, which shows the problems to the agent so it fixes the spec. Anything else exits 0.
It reads the hook payload (JSON) on stdin; it changes no file.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

if {"-h", "--help"} & set(sys.argv[1:]):
    print(__doc__)
    raise SystemExit(0)

try:
    from svgforge.lint import lint
except ImportError:  # running from a clone or the plugin folder: use the source beside this file
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from svgforge.lint import lint


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    path = Path((payload.get("tool_input") or {}).get("file_path") or "")
    if path.suffix.lower() != ".svg" or not path.is_file():
        return 0
    problems = lint(path.name, path.read_text(encoding="utf-8"))
    if not problems:
        return 0
    print("svgforge lint found problems in " + str(path) + ":\n  " + "\n  ".join(problems)
          + "\nFix the figure's spec and rebuild it; do not edit the SVG by hand.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
