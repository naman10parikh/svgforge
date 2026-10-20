# Svgforge: learnings

Every mistake becomes a rule. Append only, newest last.

## 2026-10-19: the first release

- **Three accents in one figure meant none stood out.** The first loop example drew the gate card, the proposal
  arrow and the base bar in the accent colour. Rule: spines and arrows stay neutral; the accent marks one thing.
- **Typed arrows render as boxes.** cairosvg, the strictest consumer, draws tofu for arrows and box-drawing
  characters. Rule: the lint fails them; draw arrows with `Canvas.arrow()` and sequences with `Canvas.seq()`.
- **A generated file can leak the machine it was built on.** An absolute output path would put a home folder into
  `INDEX.json`. Rule: generated files print paths relative to the current folder when they sit inside it.
- **Two spec folders can hold files with the same name.** Rule: load specs by file path under a module name made
  from that path; never import a spec by its bare name.
- **A script that runs its default on `--help` does real work by surprise.** Rule: every command and script here
  answers `-h` and `--help` before it reads anything else.
- **A command run from a one-step install has no repository around it.** Rule: anything a command needs at run
  time lives inside the package; that is why the example specs sit in `src/svgforge/examples/`, so
  `svgforge demo` works from `uvx`.
