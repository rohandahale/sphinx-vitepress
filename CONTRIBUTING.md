# Contributing

Thanks for helping out. This project is MIT-licensed; by contributing you
agree your work ships under the same terms.

## Setup

```bash
uv sync
uv run pytest
```

Node ≥ 20 is only needed for the tests that run VitePress itself.

## Before opening a pull request

```bash
uv run ruff check . && uv run ruff format .
uv run mypy
uv run pytest
```

Changes to the translator or the generated site must also pass the real
VitePress build, which enforces dead-link checking:

```bash
VITEPRESS_SMOKE=1 uv run pytest -m smoke tests/test_vitepress_smoke.py
```

Without `VITEPRESS_SMOKE` those tests skip, and a skipped test still exits
0, so CI additionally asserts that they reported a passing count.

## Testing conventions

- Translator and renderer changes **require** golden-file coverage: a Sphinx
  source under `tests/roots/` in, an expected `.md` out. Regenerate with
  `UPDATE_GOLDEN=1 uv run pytest tests/test_build.py`, then read the diff
  before committing it. A golden update is a claim that the new output is
  correct.
- `tests/demo/` is a small package whose docstrings are deliberately hostile
  to VitePress (Vue mustaches, angle brackets, math, doctests). Add to it when
  you fix a rendering bug, so the bug cannot come back quietly.

## Things worth knowing

- **All text escaping goes through `escape.py`.** VitePress compiles pages as
  Vue templates, so `{{ }}`, `<`, and `>` in prose are build errors. Never add
  ad-hoc escaping elsewhere.
- **The builder must never require Node.** Markdown and config generation runs
  anywhere; only the CLI shells out to npm/npx.
- **Windows is supported.** Use `posixpath` for URIs and pass list arguments to
  `subprocess` (no shell); CI runs the suite on Windows.
- Ports from other projects (sphinx-markdown-builder, DocumenterVitepress.jl,
  Makie.jl) must keep their notices. Record every one in the third-party
  section of `LICENSE` in the same commit.

## Releasing

1. Update `CHANGELOG.md`. The section for the new version becomes the
   GitHub release notes, so write it for readers.
2. Bump `version` in `pyproject.toml` and `__version__` in
   `src/sphinx_vitepress/__init__.py`. Both are checked against the tag and
   against each other, and the release fails if any of the three disagree.
   `__version__` is not cosmetic: it stamps the output directory and decides
   whether an upgrade rewrites stale markdown and theme files.
3. Tag `vX.Y.Z` and push it. The release workflow runs the full test matrix
   first, then builds, validates the metadata, publishes to PyPI via trusted
   publishing, and creates the GitHub release with the artifacts attached.
   The docs workflow deploys that version alongside the existing ones.
