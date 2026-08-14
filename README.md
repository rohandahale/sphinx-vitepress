# sphinx-vitepress

[![docs stable](https://img.shields.io/badge/docs-stable-blue.svg)](https://www.rohandahale.com/sphinx-vitepress/stable/)
[![docs dev](https://img.shields.io/badge/docs-dev-blue.svg)](https://www.rohandahale.com/sphinx-vitepress/dev/)
[![CI](https://github.com/rohandahale/sphinx-vitepress/actions/workflows/ci.yml/badge.svg)](https://github.com/rohandahale/sphinx-vitepress/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/sphinx-vitepress.svg)](https://pypi.org/project/sphinx-vitepress/)
[![Python](https://img.shields.io/pypi/pyversions/sphinx-vitepress.svg)](https://pypi.org/project/sphinx-vitepress/)
[![License](https://img.shields.io/pypi/l/sphinx-vitepress.svg)](https://github.com/rohandahale/sphinx-vitepress/blob/main/LICENSE)

A Sphinx builder that renders your documentation with [VitePress](https://vitepress.dev).
It is the Python counterpart of
[DocumenterVitepress.jl](https://github.com/LuxDL/DocumenterVitepress.jl).

Keep your `conf.py`, autodoc, NumPy-style docstrings and intersphinx
cross-references; swap classic Sphinx HTML for a modern VitePress site.

## Install

```bash
pip install sphinx-vitepress
```

Node.js 20 or newer is needed only to run VitePress itself. Generating the
markdown never requires it.

## Use

```bash
sphinx-vitepress init docs         # or point it at an existing docs/ directory
sphinx-vitepress dev docs          # live preview
sphinx-vitepress build docs _site  # production build
```

Existing projects need no changes: autodoc, napoleon, intersphinx and MyST keep
working, and `sphinx-build -b vitepress <src> <out>` works too.

Configuration, versioned deploys and the API are covered in the
[documentation](https://www.rohandahale.com/sphinx-vitepress/), which is itself
built with this package.

## License

MIT. See [LICENSE](https://github.com/rohandahale/sphinx-vitepress/blob/main/LICENSE), which also carries the notices for the
MIT-licensed projects this one adapts code from.
