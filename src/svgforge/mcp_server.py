"""svgforge's MCP server: JSON-RPC 2.0 over stdio, standard library only.

It lets any MCP client find and read a figure without rasterising it (every figure carries a full prose
description), lint an SVG, and render a folder of specs. Run: svgforge-mcp (or python3 -m svgforge.mcp_server).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from . import __version__, runlog
from .build import build, load_figures, shown
from .lint import lint
from .store import load, search
from .store import get as get_figure

PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")
INDEX_ARG = {"type": "string", "description": "Path to an INDEX.json (default: $SVGFORGE_INDEX or diagrams/INDEX.json)."}
HELP = """svgforge-mcp: svgforge's MCP server (stdio, JSON-RPC 2.0).

usage: svgforge-mcp [--help] [--version]

Tools: svgforge_list, svgforge_get, svgforge_search, svgforge_lint, svgforge_build.
Add it to a client, for example:
  claude mcp add --transport stdio svgforge -- uvx --from git+https://github.com/naman10parikh/svgforge svgforge-mcp
"""

TOOLS = [
    {"name": "svgforge_list",
     "description": "List every figure in a figure store: id, title and the document it belongs to. Start here "
                    "before drawing anything new; the figure may exist.",
     "inputSchema": {"type": "object", "properties": {
         "index": INDEX_ARG, "doc": {"type": "string", "description": "Optional filter on the document path."}}}},
    {"name": "svgforge_get",
     "description": "One figure's full record by id, including its complete prose description (alt). Read the "
                    "description instead of rasterising the SVG; it is written to carry the whole figure.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}, "index": INDEX_ARG},
                     "required": ["id"]}},
    {"name": "svgforge_search",
     "description": "Find figures whose title or description holds every term of a query (case-insensitive).",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "index": INDEX_ARG},
                     "required": ["query"]}},
    {"name": "svgforge_lint",
     "description": "Run the lint gates (text under 11px, text outside the canvas, glyphs that render as boxes, "
                    "empty alt text, a collapsed canvas, broken XML) on an SVG file or an SVG string.",
     "inputSchema": {"type": "object", "properties": {
         "path": {"type": "string", "description": "An SVG file to lint."},
         "svg": {"type": "string", "description": "Or the SVG markup itself."}}}},
    {"name": "svgforge_build",
     "description": "Render every figure spec in a folder into an output folder, lint each figure, and write "
                    "INDEX.json and a README gallery. With check=true it writes nothing and reports stale files.",
     "inputSchema": {"type": "object", "properties": {
         "figures": {"type": "string", "description": "Folder of figure specs."},
         "out": {"type": "string", "description": "Output folder (default: diagrams)."},
         "check": {"type": "boolean", "description": "Write nothing; report what is stale."}},
         "required": ["figures"]}},
]


def call(name: str, args: dict) -> tuple[str, bool]:
    """Run one tool. Returns (text, is_error)."""
    if name in ("svgforge_list", "svgforge_get", "svgforge_search"):
        path, figures = load(args.get("index"))
        if name == "svgforge_list":
            doc = (args.get("doc") or "").lower()
            rows = [f for f in figures if doc in f.get("doc", "").lower()] if doc else figures
            return "\n".join(f"{f['id']}\t{f['title']}\t{f.get('doc', '')}" for f in rows) or "no match", False
        if name == "svgforge_get":
            fig = get_figure(figures, args.get("id", ""))
            if fig is None:
                return f"no figure with id {args.get('id')!r} in {path}; use svgforge_list", True
            return json.dumps({**fig, "svg": str(path.parent / fig["file"])}, indent=2, ensure_ascii=False), False
        hits = search(figures, args.get("query", ""))
        return "\n".join(f"{f['id']}\t{f['title']}" for f in hits) or "no match", False
    if name == "svgforge_lint":
        if args.get("path"):
            svg, fid = Path(args["path"]).read_text(encoding="utf-8"), Path(args["path"]).name
        elif args.get("svg"):
            svg, fid = args["svg"], "svg"
        else:
            return "give a path or an svg string", True
        problems = lint(fid, svg)
        return ("\n".join(problems) if problems else "OK: passes every lint gate"), bool(problems)
    if name == "svgforge_build":
        out = args.get("out") or "diagrams"
        regen = f"svgforge build {shown(args['figures'])} --out {shown(out)}"
        res = build(load_figures(args["figures"]), out, regen, check=bool(args.get("check")))
        lines = [f"{f['id']}\t{f['bytes']} B\t{f['title']}" for f in res.index]
        lines += [f"problem: {p}" for p in res.problems] + [f"stale: {s}" for s in res.stale]
        lines.append(f"{len(res.index)} figure(s); {'ok' if res.ok else 'not ok'}"
                     + ("" if args.get("check") else f"; wrote {len(res.written)} file(s) to {out}"))
        return "\n".join(lines), not res.ok
    return f"unknown tool {name!r}", True


def send(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def handle(req: dict) -> dict | None:
    method, rid = req.get("method"), req.get("id")
    if rid is None:  # a notification: no reply
        return None
    if method == "initialize":
        asked = (req.get("params") or {}).get("protocolVersion")
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": asked if asked in PROTOCOLS else PROTOCOLS[1],
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "svgforge", "version": __version__}}}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = req.get("params") or {}
        name, started = params.get("name", ""), time.monotonic()
        try:
            text, is_error = call(name, params.get("arguments") or {})
        except Exception as exc:  # report to the client; never kill the server
            text, is_error = f"error: {exc}", True
        runlog.append(f"mcp:{name}", started, "fail" if is_error else "ok")
        return {"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": text}],
                                                         "isError": is_error}}
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"method not found: {method}"}}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if {"-h", "--help"} & set(argv):
        print(HELP)
        return 0
    if "--version" in argv:
        print(f"svgforge-mcp {__version__}")
        return 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            send({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}})
            continue
        reply = handle(req)
        if reply is not None:
            send(reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
