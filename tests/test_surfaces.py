"""The command line, the MCP server, the hook and the router, each run as a stranger would run it."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from svgforge import __version__
from svgforge.route import route

from . import ROOT

FIX = ROOT / "evals" / "fixtures"


def run(args, stdin="", env_extra=None):
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "SVGFORGE_RUNLOG": "off", **(env_extra or {})}
    return subprocess.run([sys.executable, *args], input=stdin, capture_output=True, text=True, env=env, cwd=ROOT,
                          timeout=120)


class CliTest(unittest.TestCase):
    def test_help_and_version_do_nothing_else(self):
        out = run(["-m", "svgforge", "--help"])
        self.assertEqual(out.returncode, 0)
        self.assertIn("usage: svgforge", out.stdout)
        self.assertEqual(run(["-m", "svgforge", "--version"]).stdout.strip(), f"svgforge {__version__}")
        self.assertIn("usage: svgforge-mcp", run(["-m", "svgforge.mcp_server", "--help"]).stdout)

    def test_demo_writes_three_figures_and_logs_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "runs.jsonl"
            out = run(["-m", "svgforge", "demo", "--out", f"{tmp}/demo"], env_extra={"SVGFORGE_RUNLOG": str(log)})
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertEqual(sorted(p.name for p in Path(tmp, "demo").glob("*.svg")),
                             ["loop.svg", "pipeline.svg", "stack.svg"])
            row = json.loads(log.read_text().splitlines()[-1])
            self.assertEqual((row["cmd"], row["outcome"], row["figures"]), ("demo", "ok", 3))

    def test_lint_exit_codes(self):
        self.assertEqual(run(["-m", "svgforge", "lint", str(FIX / "good" / "minimal.svg")]).returncode, 0)
        bad = run(["-m", "svgforge", "lint", str(FIX / "bad" / "tofu.svg")])
        self.assertEqual(bad.returncode, 1)
        self.assertIn("[tofu]", bad.stdout)

    def test_find_and_show_read_the_index(self):
        index = str(ROOT / "examples" / "INDEX.json")
        self.assertEqual(run(["-m", "svgforge", "find", "clockwise", "--index", index]).stdout.split("\t")[0], "loop")
        shown = json.loads(run(["-m", "svgforge", "show", "stack", "--index", index]).stdout)
        self.assertEqual(shown["id"], "stack")
        self.assertEqual(run(["-m", "svgforge", "show", "nope", "--index", index]).returncode, 1)

    def test_a_missing_index_is_a_clear_error(self):
        out = run(["-m", "svgforge", "find", "x", "--index", "no/such/INDEX.json"])
        self.assertEqual(out.returncode, 2)
        self.assertIn("no index at", out.stderr)


class McpTest(unittest.TestCase):
    def ask(self, *msgs):
        out = run(["-m", "svgforge.mcp_server"], stdin="\n".join(json.dumps(m) for m in msgs))
        return {r.get("id"): r for r in (json.loads(x) for x in out.stdout.splitlines() if x.strip())}

    def test_handshake_tools_and_calls(self):
        index = str(ROOT / "examples" / "INDEX.json")
        r = self.ask(
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "svgforge_get", "arguments": {"id": "pipeline", "index": index}}},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "svgforge_search", "arguments": {"query": "gate", "index": index}}},
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
            {"jsonrpc": "2.0", "id": 6, "method": "no/such"},
        )
        self.assertEqual(r[1]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(len(r[2]["result"]["tools"]), 5)
        record = json.loads(r[3]["result"]["content"][0]["text"])
        self.assertTrue(record["alt"].startswith("A left-to-right pipeline"))
        self.assertIn("pipeline", r[4]["result"]["content"][0]["text"])
        self.assertEqual(r[5]["result"], {})
        self.assertEqual(r[6]["error"]["code"], -32601)

    def test_build_tool_check_mode_writes_nothing(self):
        r = self.ask({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {
            "name": "svgforge_build", "arguments": {"figures": "src/svgforge/examples", "out": "examples", "check": True}}})
        self.assertFalse(r[1]["result"]["isError"], r[1]["result"]["content"][0]["text"])


class HookTest(unittest.TestCase):
    def fire(self, path):
        payload = {"tool_name": "Write", "tool_input": {"file_path": str(path)}}
        return run([str(ROOT / "hooks" / "svg_lint_hook.py")], stdin=json.dumps(payload))

    def test_a_bad_svg_is_reported_to_the_agent(self):
        out = self.fire(FIX / "bad" / "font-floor.svg")
        self.assertEqual(out.returncode, 2)
        self.assertIn("[font-floor]", out.stderr)

    def test_good_svgs_and_other_files_pass(self):
        self.assertEqual(self.fire(FIX / "good" / "minimal.svg").returncode, 0)
        self.assertEqual(self.fire(ROOT / "README.md").returncode, 0)
        self.assertEqual(run([str(ROOT / "hooks" / "svg_lint_hook.py")], stdin="not json").returncode, 0)


class RouteTest(unittest.TestCase):
    def test_routes(self):
        self.assertEqual(route("turn this ASCII diagram into a figure")["skill"], "ascii-to-figure")
        self.assertEqual(route("review this figure, the labels overlap")["skill"], "figure-review")
        self.assertEqual(route("is there an existing figure of the release flow")["route"], "find")
        self.assertEqual(route("draw a picture of our deploy pipeline")["route"], "draw")
        self.assertEqual(route("something unrelated")["route"], "draw")


if __name__ == "__main__":
    unittest.main()
