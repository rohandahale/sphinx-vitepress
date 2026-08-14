# CLAUDE.md

## What this project is

**sphinx-vitepress** (working name; verified unclaimed on PyPI 2026-08-14) — the Python
equivalent of [DocumenterVitepress.jl](https://github.com/LuxDL/DocumenterVitepress.jl):
a Sphinx **builder** that emits VitePress-flavored Markdown plus a generated
`.vitepress/config.mts` and theme, so any Sphinx project (autodoc + napoleon +
intersphinx + MyST) gets a modern VitePress site instead of classic Sphinx HTML.
A CLI (`sphinx-vitepress init|dev|build|deploy`) orchestrates the Node/VitePress build
and versioned GitHub Pages deploys.

Structural analogy: `Sphinx : sphinx-vitepress :: Documenter.jl : DocumenterVitepress.jl`.

**Visual target:** https://luxdl.github.io/DocumenterVitepress.jl/stable/ — theme parity
with that site is an explicit goal (milestone M3).

## Source of truth

- `DESIGN.md` — full verified architecture, milestones M0–M5, risk register. Read it
  before implementing anything.
- `DocumenterVitepress.jl-0.3.5/` — local copy of the reference implementation
  (gitignored, MIT). Consult it instead of guessing:
  - `src/writer.jl` — the markdown flavor to emit (admonitions, `{#id}` anchors,
    docstring `<details>` blocks, `<`/`>` escaping)
  - `src/vitepress_config.jl` — config.mts generation via placeholder substitution
  - `src/frontmatter.jl` — YAML frontmatter merging
  - `src/DocumenterVitepress.jl` — versioned deploy (bases.txt / siteinfo.js / versions.js)
  - `template/src/.vitepress/` — theme, CSS, VersionPicker.vue, config template

## Status

**M0 + M1 + M2 done** (2026-08-14): one command works end to end —
`sphinx-vitepress build <src>` runs Sphinx (autodoc + napoleon + MyST), emits
VitePress markdown **plus a generated `.vitepress/config.mts`** (sidebar/nav
derived from the toctree) **and `package.json`**, then npm-installs and runs
the real `vitepress build`, green with strict dead links (opt-in smoke test).
`sphinx-vitepress init|dev|build` are real; `deploy` is an honest stub.
A user `.vitepress/` dir in the source overrides the bundled template
(placeholders still substituted). Frontmatter was deferred from M2 to M3
(VitePress derives titles from the h1, so nothing needed it yet).
**M3 done** (2026-08-14): DocumenterVitepress theme ported (style.css /
docstrings.css / theme index.ts → `template/theme/`, attribution in NOTICE.md);
autodoc objects now render as `<details class="docstring custom-block">` with
anchored summary bindings + `<Badge>` type labels + fenced signatures
(`vitepress_docstring_style = "headings"` restores plain headings); fixed the
napoleon `literal_emphasis` adjacent-italics bug that rendered `*[*` asterisk
soup in Parameters lists. Next: **M4** — objects.inv emission + versioned
deploy (+ source-link badges via viewcode/linkcode). See DESIGN.md §F.

## Architecture in one paragraph

Sphinx does all extraction and cross-reference resolution (autodoc, napoleon,
intersphinx, MyST are read-side extensions — zero work for us; users keep their
`conf.py`). Our `VitepressBuilder`/`VitepressTranslator` subclass
`sphinx-markdown-builder` (MIT, pinned `>=0.6.10,<0.7`) and emit VitePress markdown;
`finish()` generates the sidebar/nav from `env.toctree_includes` + `env.titles`,
renders `config.mts` from a placeholder template, copies the theme, and writes
`objects.inv` via `sphinx.util.inventory.InventoryFile.dump`. Node is never required
at markdown-emission time — only the CLI shells out to `npm` / `npx vitepress`.
Target VitePress 1.6.x; CI tracks 2.0-alpha.

## Conventions

- Python ≥ 3.11; `uv` for everything; hatchling backend; src layout
- Lint/format: `uv run ruff check .` + `uv run ruff format .` before finishing a task;
  mypy on `src/`
- Tests: pytest; translator/renderer changes REQUIRE golden-file tests
  (Sphinx source in → expected `.md` out)
- Docstrings in this codebase: NumPy style, full type hints
- Windows is a supported platform: subprocess with list args (no shell), `posixpath`
  for URIs, resolve `npm.cmd` on Windows
- The top recurring bug class will be Vue-safety: `{{ }}`, `<`/`>`, and raw HTML in
  generated markdown are compiled by Vue and can fail the VitePress build. ALL text
  escaping goes through `escape.py` — never inline ad-hoc escaping.

## Commands

- `uv sync` · `uv run pytest` · `uv run ruff check . && uv run ruff format .` · `uv run mypy`
- `UPDATE_GOLDEN=1 uv run pytest tests/test_build.py` — regenerate goldens after an
  intentional output change (then eyeball the diff before committing)
- `VPDEMO_OFFLINE=1 uv run sphinx-build -b vitepress demo/docs demo/build/markdown` —
  build the demo's markdown (offline mode skips the intersphinx fetch)
- `VITEPRESS_SMOKE=1 uv run pytest tests/test_vitepress_smoke.py` — full proof:
  npm install + `vitepress build` over the demo, strict dead links (needs node ≥ 20)
- `uv run sphinx-vitepress dev demo/docs` — live preview of the demo site
- `uv run sphinx-vitepress build <src> [out] [--no-build]` — full build
  (`--no-build` stops after markdown + config; no Node needed)

## Hard-won facts (do not re-litigate)

- `sphinx-vitepress` and `sphinx-notes-vitepress` did NOT exist on PyPI (2026-08-14);
  the original research for this project came from a Gemini chat that fabricated them.
  Verify EVERY new dependency at `https://pypi.org/pypi/<name>/json` before adding it.
- Intersphinx costs the builder nothing: by `write_doc` time, external refs are plain
  `reference` nodes with absolute `refuri`.
- VitePress fails builds on dead links by default, and compiles `{{ }}`/raw HTML in
  prose as Vue templates; fenced code blocks are auto-`v-pre`.
- Licensing: ours is MIT. Porting code/CSS from sphinx-markdown-builder (MIT),
  DocumenterVitepress.jl (MIT), or Makie's VersionPicker.vue (MIT) requires keeping
  their notices — record every port in NOTICE.md in the same commit.
