import json
import tempfile
import unittest
from pathlib import Path

from svgforge.build import EXAMPLES, build, load_figures
from svgforge.lint import lint, rules_hit

from . import ROOT

FIX = ROOT / "evals" / "fixtures"


class LintTest(unittest.TestCase):
    def test_each_bad_fixture_hits_its_rule(self):
        golden = json.loads((ROOT / "evals" / "golden.json").read_text())
        for name, want in golden["bad"].items():
            with self.subTest(name=name):
                self.assertEqual(rules_hit(lint(name, (FIX / "bad" / name).read_text())), want)

    def test_good_fixture_and_examples_pass(self):
        for path in [FIX / "good" / "minimal.svg", *sorted((ROOT / "examples").glob("*.svg"))]:
            with self.subTest(path=path.name):
                self.assertEqual(lint(path.name, path.read_text()), [])


class BuildTest(unittest.TestCase):
    def test_examples_load_in_name_order(self):
        self.assertEqual([f["id"] for f in load_figures(EXAMPLES)], ["loop", "pipeline", "stack"])

    def test_build_is_deterministic_and_idempotent(self):
        figures = load_figures(EXAMPLES)
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = build(figures, a, "regen")
            self.assertTrue(first.ok)
            self.assertEqual(sorted(first.written), ["INDEX.json", "README.md", "loop.svg", "pipeline.svg", "stack.svg"])
            build(figures, b, "regen")
            for p in Path(a).iterdir():
                self.assertEqual(p.read_bytes(), (Path(b) / p.name).read_bytes())
            self.assertEqual(build(figures, a, "regen").written, [])

    def test_check_reports_stale_and_writes_nothing(self):
        figures = load_figures(EXAMPLES)
        with tempfile.TemporaryDirectory() as tmp:
            build(figures, tmp, "regen")
            (Path(tmp) / "loop.svg").write_text("<svg/>")
            res = build(figures, tmp, "regen", check=True)
            self.assertEqual(res.stale, ["loop.svg"])
            self.assertFalse(res.ok)
            self.assertEqual((Path(tmp) / "loop.svg").read_text(), "<svg/>")

    def test_only_renders_a_subset_and_leaves_the_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            res = build(load_figures(EXAMPLES), tmp, "regen", only=["loop"])
            self.assertEqual(res.written, ["loop.svg"])
            self.assertFalse((Path(tmp) / "INDEX.json").exists())
            with self.assertRaises(ValueError):
                build(load_figures(EXAMPLES), tmp, "regen", only=["nope"])

    def test_index_records_alt_and_regenerate(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(load_figures(EXAMPLES), tmp, "svgforge demo --out x")
            index = json.loads((Path(tmp) / "INDEX.json").read_text())
            self.assertEqual(index["count"], 3)
            self.assertEqual(index["regenerate"], "svgforge demo --out x")
            self.assertTrue(all(len(f["alt"].split()) >= 80 for f in index["figures"]))

    def test_duplicate_ids_and_missing_folders_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = "from svgforge import Canvas\nFIGURES = [{'id': 'same', 'title': 't', 'build': lambda: ('', '')}]\n"
            (Path(tmp) / "a.py").write_text(spec)
            (Path(tmp) / "b.py").write_text(spec)
            with self.assertRaises(ValueError):
                load_figures(tmp)
        with self.assertRaises(FileNotFoundError):
            load_figures(ROOT / "no-such-folder")

    def test_helper_files_are_not_specs(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "_common.py").write_text("LABEL = 'shared'\n")
            (Path(tmp) / "one.py").write_text(
                "from _common import LABEL\nFIGURES = [{'id': 'one', 'title': LABEL, 'build': lambda: ('', '')}]\n")
            self.assertEqual([f["title"] for f in load_figures(tmp)], ["shared"])


if __name__ == "__main__":
    unittest.main()
