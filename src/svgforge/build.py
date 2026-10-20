"""Render figure specs to SVG, lint every one, and write INDEX.json and a README gallery beside them.

A figure spec is a Python file that exports FIGURES, a list of dicts with:
  id      kebab-case file stem, also the INDEX.json key
  title   the figure's title
  build   a callable returning (svg_string, alt_text)
  doc     optional: the document the figure belongs to
  anchor  optional: the heading it sits under in that document
Files whose names start with "_" are helpers and are not loaded as specs. Output is deterministic: the same specs
give byte-identical files, so `check` can tell a stale figure from a current one.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .lint import lint

EXAMPLES = Path(__file__).resolve().parent / "examples"


@dataclass
class BuildResult:
    index: list[dict] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    stale: list[str] = field(default_factory=list)
    written: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems and not self.stale


def load_figures(figures_dir: str | Path) -> list[dict]:
    """Import every spec file in a folder, in name order, and return its figures."""
    folder = Path(figures_dir)
    if not folder.is_dir():
        raise FileNotFoundError(f"no figures folder at {folder}")
    out: list[dict] = []
    sys.path.insert(0, str(folder.resolve()))  # a spec may import a helper beside it
    try:
        for f in sorted(folder.glob("*.py")):
            if f.name.startswith("_"):
                continue
            name = "svgforge_spec_" + hashlib.sha1(str(f.resolve()).encode()).hexdigest()[:12]
            spec = importlib.util.spec_from_file_location(name, f)
            if spec is None or spec.loader is None:
                raise ImportError(f"cannot load {f}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            for fig in getattr(mod, "FIGURES", []):
                missing = [k for k in ("id", "title", "build") if k not in fig]
                if missing:
                    raise ValueError(f"{f.name}: a figure has no {', '.join(missing)}")
                out.append({**fig, "_spec": f.name})
    finally:
        sys.path.remove(str(folder.resolve()))
    seen: dict[str, str] = {}
    for fig in out:
        if fig["id"] in seen:
            raise ValueError(f"duplicate figure id {fig['id']!r} in {fig['_spec']} and {seen[fig['id']]}")
        seen[fig["id"]] = fig["_spec"]
    return out


def shown(path: str | Path) -> str:
    """A path as a command should print it: relative to the current folder when it sits inside it."""
    rel = os.path.relpath(Path(path).resolve())
    return rel if not rel.startswith("..") else str(path)


def build(figures: list[dict], out_dir: str | Path, regenerate: str = "", check: bool = False,
          only: list[str] | None = None) -> BuildResult:
    """Render, lint and write. With `check`, write nothing and list every file that would change."""
    out = Path(out_dir)
    picked = [f for f in figures if not only or f["id"] in only]
    if only and not picked:
        raise ValueError(f"no figure matched {', '.join(only)}")
    r = BuildResult()
    for fig in picked:
        svg, alt = fig["build"]()
        r.problems += lint(fig["id"], svg)
        _emit(out / f"{fig['id']}.svg", svg, check, r)
        r.index.append({"id": fig["id"], "title": fig["title"], "doc": fig.get("doc", ""),
                        "anchor": fig.get("anchor", ""), "file": f"{fig['id']}.svg", "alt": alt,
                        "bytes": len(svg.encode())})
    if not only:  # the index and the gallery describe the whole set, so a partial build leaves them alone
        _emit(out / "INDEX.json", index_json(r.index, regenerate), check, r)
        _emit(out / "README.md", gallery(r.index, regenerate), check, r)
    return r


def _emit(path: Path, text: str, check: bool, r: BuildResult) -> None:
    prev = path.read_text(encoding="utf-8") if path.exists() else None
    if prev == text:
        return
    if check:
        r.stale.append(path.name)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    r.written.append(path.name)


def index_json(index: list[dict], regenerate: str) -> str:
    return json.dumps({"generator": "svgforge", "regenerate": regenerate, "count": len(index), "figures": index},
                      indent=2, ensure_ascii=False) + "\n"


def gallery(index: list[dict], regenerate: str) -> str:
    lines = ["# Figures", "",
             "Rendered by svgforge from Python specs. Each SVG is self-contained. Its full description is the `alt` "
             "in `INDEX.json`, and the same text is in the SVG's `<desc>` and `aria-label`, so an agent can read the "
             "figure without looking at it.", ""]
    if regenerate:
        lines += ["```bash", regenerate, "```", ""]
    lines += [f"**{len(index)} figures.**", ""]
    for f in index:
        first = f["alt"].split(". ")[0].rstrip(".")
        where = f" · in {f['doc']}" + (f" under _{f['anchor']}_" if f["anchor"] else "") if f["doc"] else ""
        lines += [f"## {f['title']}", "", f"`{f['id']}`{where}", "", f"![{first}]({f['file']})", "", f"{first}.", ""]
    return "\n".join(lines)
