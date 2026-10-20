"""The svgforge command line. Every command answers --help; nothing runs before the arguments are read."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import __version__, runlog
from .build import EXAMPLES, build, load_figures, shown
from .lint import lint
from .route import route
from .store import load, search
from .store import get as get_figure

DESCRIPTION = "Diagrams as code: deterministic SVG figures with lint gates, drawn by agents."
EPILOG = """examples:
  svgforge demo --out /tmp/demo                 render the three bundled example figures
  svgforge build figures --out diagrams         render every spec in figures/ into diagrams/
  svgforge build figures --out diagrams --check fail if a committed SVG is stale (for CI)
  svgforge lint diagrams/*.svg                  run the lint gates on any SVG
  svgforge find "release gate"                  search diagrams/INDEX.json
  svgforge route "turn this ascii diagram into a figure"

Write a spec: see AUTHORING.md in the repository. The MCP server is svgforge-mcp."""


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="svgforge", description=DESCRIPTION, epilog=EPILOG,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"svgforge {__version__}")
    sub = p.add_subparsers(dest="cmd", metavar="<command>")

    b = sub.add_parser("build", help="render every spec in a folder, lint each figure, write INDEX.json and a gallery")
    b.add_argument("figures", nargs="?", default="figures", help="folder of figure specs (default: figures)")
    b.add_argument("--out", default="diagrams", help="output folder (default: diagrams)")
    b.add_argument("--only", nargs="+", metavar="ID", help="render only these figure ids")
    b.add_argument("--check", action="store_true", help="write nothing; exit 1 if any output is stale")
    b.add_argument("--json", action="store_true", help="print the result as JSON")

    li = sub.add_parser("lint", help="run the lint gates on SVG files")
    li.add_argument("files", nargs="+", help="SVG files")
    li.add_argument("--json", action="store_true", help="print the problems as JSON")

    d = sub.add_parser("demo", help="render the three bundled example figures into a folder")
    d.add_argument("--out", default="svgforge-demo", help="output folder (default: svgforge-demo)")

    f = sub.add_parser("find", help="search a figure store by title and description")
    f.add_argument("query", nargs="+", help="terms; every term must appear")
    f.add_argument("--index", help="path to INDEX.json (default: $SVGFORGE_INDEX or diagrams/INDEX.json)")

    s = sub.add_parser("show", help="print one figure's record, with its full description")
    s.add_argument("id", help="figure id")
    s.add_argument("--index", help="path to INDEX.json (default: $SVGFORGE_INDEX or diagrams/INDEX.json)")

    r = sub.add_parser("route", help="name the skill and the command for a task in plain words")
    r.add_argument("task", nargs="+", help="the task, in plain words")
    r.add_argument("--json", action="store_true", help="print the route as JSON")

    ru = sub.add_parser("runs", help="show the run log")
    ru.add_argument("--last", type=int, default=20, help="how many runs (default: 20)")
    return p


def report_build(res, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"ok": res.ok, "figures": [{k: f[k] for k in ("id", "title", "bytes")} for f in res.index],
                          "written": res.written, "stale": res.stale, "problems": res.problems}, indent=2))
    else:
        for f in res.index:
            flag = "~" if f"{f['id']}.svg" in res.written or f"{f['id']}.svg" in res.stale else "="
            print(f" {flag} {f['id']:<36} {f['bytes']:>8,} B   {f['title'][:48]}")
        for p in res.problems:
            print("  problem: " + p)
        if res.stale:
            print("  stale: " + ", ".join(res.stale) + " (run the build without --check)")
        print(f"{len(res.index)} figure(s), {len(res.problems)} problem(s)" + (", stale" if res.stale else ""))
    return 0 if res.ok else 1


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    started = time.monotonic()
    if args.cmd is None:
        parser().print_help()
        return 0
    try:
        code, facts = run(args)
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"svgforge: {exc}", file=sys.stderr)
        runlog.append(args.cmd, started, "error", error=str(exc)[:200])
        return 2
    if args.cmd != "runs":
        runlog.append(args.cmd, started, "ok" if code == 0 else "fail", **facts)
    return code


def run(args: argparse.Namespace) -> tuple[int, dict]:
    if args.cmd == "build":
        regen = f"svgforge build {shown(args.figures)} --out {shown(args.out)}"
        res = build(load_figures(args.figures), args.out, regen, check=args.check, only=args.only)
        return report_build(res, args.json), {"figures": len(res.index), "problems": len(res.problems),
                                              "stale": len(res.stale), "check": args.check}
    if args.cmd == "demo":
        res = build(load_figures(EXAMPLES), args.out, f"svgforge demo --out {shown(args.out)}")
        code = report_build(res, False)
        print(f"wrote {Path(args.out)}/: open README.md there to see the figures")
        return code, {"figures": len(res.index), "problems": len(res.problems)}
    if args.cmd == "lint":
        problems = []
        for name in args.files:
            problems += lint(Path(name).name, Path(name).read_text(encoding="utf-8"))
        if args.json:
            print(json.dumps({"ok": not problems, "files": len(args.files), "problems": problems}, indent=2))
        else:
            print("\n".join(problems) if problems else f"OK: {len(args.files)} file(s) pass the lint gates")
        return (1 if problems else 0), {"files": len(args.files), "problems": len(problems)}
    if args.cmd == "find":
        _, figures = load(args.index)
        hits = search(figures, " ".join(args.query))
        print("\n".join(f"{f['id']}\t{f['title']}" for f in hits) or "no match")
        return 0, {"hits": len(hits)}
    if args.cmd == "show":
        path, figures = load(args.index)
        fig = get_figure(figures, args.id)
        if fig is None:
            print(f"no figure with id {args.id!r} in {path}", file=sys.stderr)
            return 1, {"found": False}
        print(json.dumps({**fig, "svg": str(path.parent / fig["file"])}, indent=2, ensure_ascii=False))
        return 0, {"found": True}
    if args.cmd == "route":
        r = route(" ".join(args.task))
        print(json.dumps(r, indent=2) if args.json else f"skill: {r['skill']}\ncommand: {r['command']}\nwhy: {r['why']}")
        return 0, {"route": r["route"]}
    if args.cmd == "runs":
        rows = runlog.tail(args.last)
        print("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) or f"no runs logged yet ({runlog.log_path()})")
        return 0, {}
    raise ValueError(f"unknown command {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
