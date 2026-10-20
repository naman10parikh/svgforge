#!/usr/bin/env python3
"""svgforge's evals: structural checks and golden tasks, each one pass or fail.

  python3 evals/run.py          run every eval; exit 1 on any failure
  python3 evals/run.py --json   print the results as JSON

L1 structural: the bundled examples build, pass every lint gate, come out byte-identical three runs in a row
   (pass^3), and the committed examples/ folder is current.
L2 golden tasks (evals/golden.json): each bad fixture is flagged with exactly its rule and each good fixture
   passes; precision, recall and F1 over the rule hits must all be 1.0.
MCP: the server answers initialize and tools/list with its five tools, and lints a bad fixture over stdio.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("SVGFORGE_RUNLOG", "off")

from svgforge.build import EXAMPLES, build, load_figures  # noqa: E402
from svgforge.lint import lint, rules_hit  # noqa: E402

FIX = ROOT / "evals" / "fixtures"
REGEN = "svgforge build src/svgforge/examples --out examples"


def structural() -> list[tuple[str, bool, str]]:
    out = []
    figures = load_figures(EXAMPLES)
    out.append(("examples-load", len(figures) == 3, f"{len(figures)} figures from the bundled specs"))
    renders = []
    for _ in range(3):
        with tempfile.TemporaryDirectory() as tmp:
            res = build(figures, tmp, REGEN)
            renders.append({p.name: p.read_bytes() for p in sorted(Path(tmp).iterdir())})
            problems = res.problems
    out.append(("examples-lint-clean", not problems, "; ".join(problems) or "0 problems"))
    same = all(r == renders[0] for r in renders[1:])
    out.append(("deterministic-pass^3", same, "three builds, byte-identical" if same else "builds differ"))
    current = build(figures, ROOT / "examples", REGEN, check=True)
    out.append(("examples-current", not current.stale,
                "examples/ matches the specs" if not current.stale else "stale: " + ", ".join(current.stale)))
    return out


def golden() -> list[tuple[str, bool, str]]:
    spec = json.loads((FIX.parent / "golden.json").read_text())
    out, tp, fp, fn = [], 0, 0, 0
    for name, want in spec["bad"].items():
        got = rules_hit(lint(name, (FIX / "bad" / name).read_text()))
        tp += len(set(got) & set(want))
        fp += len(set(got) - set(want))
        fn += len(set(want) - set(got))
        out.append((f"golden-bad-{name}", got == want, f"want {want}, got {got}"))
    goods = [(FIX / "good" / n) for n in spec["good"]] + sorted((ROOT / "examples").glob("*.svg"))
    for path in goods:
        got = rules_hit(lint(path.name, path.read_text()))
        fp += len(got)
        out.append((f"golden-good-{path.name}", not got, f"got {got}" if got else "passes"))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    out.append(("golden-f1", f1 == 1.0, f"precision {precision:.2f} recall {recall:.2f} F1 {f1:.2f}"))
    return out


def mcp() -> list[tuple[str, bool, str]]:
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "svgforge_lint", "arguments": {"path": str(FIX / "bad" / "tofu.svg")}}},
    ]
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    proc = subprocess.run([sys.executable, "-m", "svgforge.mcp_server"], input="\n".join(json.dumps(m) for m in msgs),
                          capture_output=True, text=True, env=env, timeout=60)
    replies = {r["id"]: r for r in (json.loads(x) for x in proc.stdout.splitlines() if x.strip())}
    tools = [t["name"] for t in replies.get(2, {}).get("result", {}).get("tools", [])]
    lint_reply = replies.get(3, {}).get("result", {})
    text = (lint_reply.get("content") or [{}])[0].get("text", "")
    return [
        ("mcp-initialize", replies.get(1, {}).get("result", {}).get("serverInfo", {}).get("name") == "svgforge",
         "serverInfo.name is svgforge"),
        ("mcp-tools-list", len(tools) == 5, ", ".join(tools)),
        ("mcp-lint-call", lint_reply.get("isError") is True and "[tofu]" in text, text[:80]),
    ]


def main() -> int:
    if {"-h", "--help"} & set(sys.argv[1:]):
        print(__doc__)
        return 0
    results = structural() + golden() + mcp()
    failed = [r for r in results if not r[1]]
    if "--json" in sys.argv:
        print(json.dumps({"passed": len(results) - len(failed), "failed": len(failed),
                          "results": [{"eval": n, "ok": ok, "detail": d} for n, ok, d in results]}, indent=2))
    else:
        for name, ok, detail in results:
            print(f"{'PASS' if ok else 'FAIL'}  {name:<32} {detail}")
        print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
