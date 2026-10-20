"""Read a figure store: the INDEX.json that `svgforge build` writes beside its SVGs.

The index path comes from the caller, else $SVGFORGE_INDEX, else diagrams/INDEX.json in the current folder.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULT_INDEX = "diagrams/INDEX.json"


def index_path(given: str | None = None) -> Path:
    return Path(given or os.environ.get("SVGFORGE_INDEX") or DEFAULT_INDEX)


def load(given: str | None = None) -> tuple[Path, list[dict]]:
    path = index_path(given)
    if not path.exists():
        raise FileNotFoundError(f"no index at {path}: run `svgforge build` first, or pass the path to an INDEX.json")
    return path, json.loads(path.read_text(encoding="utf-8")).get("figures", [])


def search(figures: list[dict], query: str) -> list[dict]:
    """Figures whose title or alt text holds every term of the query (case-insensitive)."""
    terms = query.lower().split()
    return [f for f in figures if terms and all(t in (f["title"] + " " + f["alt"]).lower() for t in terms)]


def get(figures: list[dict], fid: str) -> dict | None:
    return next((f for f in figures if f["id"] == fid), None)
