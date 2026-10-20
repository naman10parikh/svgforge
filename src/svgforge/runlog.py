"""The run log: one JSON line per command, append-only, so every build and lint leaves a trace.

Where it goes: $SVGFORGE_RUNLOG if set (set it to "off" to turn the log off), else
$XDG_STATE_HOME/svgforge/runs.jsonl, else ~/.local/state/svgforge/runs.jsonl. No model is called, so a run costs
no tokens; the log records what ran, how long it took and what it found.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def log_path() -> Path | None:
    env = os.environ.get("SVGFORGE_RUNLOG")
    if env is not None:
        return None if env.strip().lower() in ("", "off", "0", "false") else Path(env).expanduser()
    state = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(state) / "svgforge" / "runs.jsonl"


def append(cmd: str, started: float, outcome: str, **facts: object) -> None:
    """Write one line. A log that cannot be written never fails the command it records."""
    path = log_path()
    if path is None:
        return
    row = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "cmd": cmd,
           "duration_ms": round((time.monotonic() - started) * 1000), "outcome": outcome, **facts}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"svgforge: run log not written ({exc})", file=sys.stderr)


def tail(n: int = 20) -> list[dict]:
    """The last n lines of the log, oldest first."""
    path = log_path()
    if path is None or not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[-n:]:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    return rows
