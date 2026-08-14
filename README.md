# sphinx-vitepress

A Sphinx builder that renders your documentation with [VitePress](https://vitepress.dev) —
[DocumenterVitepress.jl](https://github.com/LuxDL/DocumenterVitepress.jl) for Python.

Keep your `conf.py`, autodoc, NumPy-style docstrings, and intersphinx cross-references;
swap classic Sphinx HTML for a modern VitePress site.

**Status:** pre-alpha, working. `sphinx-vitepress build docs` produces a
complete VitePress site: markdown, generated config, theme, and `objects.inv`.
See [DESIGN.md](DESIGN.md) for the architecture, milestones, and risk register.

## Quick start

```bash
pip install sphinx-vitepress          # not yet published; use a git checkout
sphinx-vitepress init docs            # or point it at an existing docs/ dir
sphinx-vitepress dev docs             # live preview
sphinx-vitepress build docs _site     # production build
```

Existing Sphinx projects need no changes: autodoc, napoleon, intersphinx and
MyST keep working, and `sphinx-build -b vitepress <src> <out>` also works
directly.

## Configuration

All settings are optional; `html_logo`, `html_favicon` and `copyright` are
picked up from your existing Sphinx config.

| Setting | Purpose |
| --- | --- |
| `vitepress_repo` | GitHub icon in the navbar and per-page edit links |
| `vitepress_accent` | accent palette: a preset (`blue`, `afmhot`, `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `ocean`), a hex color, four hex stops, or `{"light": …, "dark": …}` |
| `vitepress_frontmatter` | per-page VitePress frontmatter — use `{"index": {"layout": "home", "hero": {…}}}` for a hero landing page |
| `vitepress_docstring_style` | `"details"` (collapsible API cards, default) or `"headings"` |
| `vitepress_inline_toctree` | keep Sphinx's inline toctree lists (off by default; the sidebar already has them) |
| `vitepress_base`, `vitepress_title`, `vitepress_description` | site basics |

Versioned deploys:

```bash
sphinx-vitepress deploy docs --deploy-dir _site --release v1.2.3 --repo-base /my-repo/
```

## License

MIT — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
