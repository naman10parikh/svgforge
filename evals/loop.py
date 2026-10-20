#!/usr/bin/env python3
"""svgforge's improvement loop: run the evals, read the figure corpus for gaps, and write proposals.

  python3 evals/loop.py [--out proposals/latest.md] [--svgs DIR ...]

It never edits the engine and never commits: a person reads the proposals and makes every change. Two checks:
  1. the evals (evals/run.py): a failure becomes a proposal to fix the regression, and the loop exits 1;
  2. the corpus (examples/ plus any --svgs folder): every glyph that the width table does not know is measured
     with a fallback width, so a label holding it may wrap early or overflow; each one becomes a proposal.
With GITHUB_OUTPUT set, it writes propose=true or propose=false for the workflow that opens the issue.
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from svgforge.text import unmeasured  # noqa: E402


def evals() -> tuple[bool, dict]:
    proc = subprocess.run([sys.executable, str(ROOT / "evals" / "run.py"), "--json"], capture_output=True, text=True,
                          env={**os.environ, "SVGFORGE_RUNLOG": "off"}, timeout=300)
    try:
        report = json.loads(proc.stdout)
    except ValueError:
        report = {"passed": 0, "failed": 1, "results": [{"eval": "run.py", "ok": False, "detail": proc.stderr[-300:]}]}
    return proc.returncode == 0, report


def corpus_gaps(folders: list[Path]) -> dict[str, list[str]]:
    """Each unmeasured glyph, with the figures whose text nodes use it."""
    gaps: dict[str, set[str]] = {}
    for folder in folders:
        for svg in sorted(folder.glob("*.svg")):
            for body in re.findall(r"<text[^>]*>(.*?)</text>", svg.read_text(encoding="utf-8"), flags=re.S):
                for ch in unmeasured(html.unescape(body)):
                    gaps.setdefault(ch, set()).add(svg.name)
    return {ch: sorted(names) for ch, names in sorted(gaps.items())}


def write(out: Path, ok: bool, report: dict, gaps: dict[str, list[str]]) -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# svgforge improvement loop", "",
             f"Run {stamp}. Evals: {report['passed']} passed, {report['failed']} failed.", ""]
    n = 0
    for r in report["results"]:
        if not r["ok"]:
            n += 1
            lines += [f"## {n}. Fix the regression in `{r['eval']}`", "", f"The eval failed: {r['detail']}", "",
                      "Reproduce with `python3 evals/run.py`, fix the cause, and add a test that would have caught it.",
                      ""]
    for ch, names in gaps.items():
        n += 1
        lines += [f"## {n}. Measure {ch!r} (U+{ord(ch):04X}) exactly", "",
                  f"The width table in `src/svgforge/text.py` has no entry for it, so it is measured with the fallback "
                  f"width. It appears in: {', '.join(names)}. Add its advance width to `_W`, rebuild the examples "
                  "(`svgforge build src/svgforge/examples --out examples`) and run the evals.", ""]
    if not n:
        lines += ["Nothing to propose: every eval passes and every glyph in the corpus is measured.", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return n


def main() -> int:
    args = sys.argv[1:]
    if {"-h", "--help"} & set(args):
        print(__doc__)
        return 0
    out = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / "proposals" / "latest.md"
    folders = [ROOT / "examples"] + [Path(args[i + 1]) for i, a in enumerate(args) if a == "--svgs"]
    ok, report = evals()
    n = write(out, ok, report, corpus_gaps(folders))
    print(f"evals {'pass' if ok else 'FAIL'}; {n} proposal(s) written to {out}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"propose={'true' if n else 'false'}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
