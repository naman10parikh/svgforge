@AGENTS.md

# svgforge: notes for Claude Code

- **The hook.** `.claude/settings.json` runs `hooks/svg_lint_hook.py` after every Write or Edit. When you write an
  `.svg` that fails a lint gate it exits 2 and shows you the problems. Fix the spec and rebuild; never hand-edit
  the SVG. The plugin ships the same hook in `hooks/hooks.json`.
- **The MCP server.** `.mcp.json` runs the server from GitHub through `uvx`. To try your local changes, start
  Claude Code with `claude --mcp-config .mcp.dev.json`, which runs the server from `src/` against
  `examples/INDEX.json`.
- **Sub-agents.** Hand a new figure to `figure-author` and a review to `figure-critic`; the critic changes nothing.
- **Before you finish:** `python3 -m unittest && python3 evals/run.py`. If you changed a bundled example, rebuild
  `examples/` with `PYTHONPATH=src python3 -m svgforge build src/svgforge/examples --out examples` and read the
  PNGs.
- **Code style.** Standard library only in `src/` (the `e2b` package is optional and used only by `sandbox/`), named
  functions over clever ones, files under 400 lines.
- **No model ID anywhere.** svgforge calls no model.
