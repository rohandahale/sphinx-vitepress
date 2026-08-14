# sphinx-vitepress

**sphinx-vitepress** is a [Sphinx](https://www.sphinx-doc.org) builder that emits
[VitePress](https://vitepress.dev)-flavored Markdown, a generated
`.vitepress/config.mts`, and a theme — so an existing Sphinx project becomes a
modern documentation site without giving up any of Sphinx's machinery.

It is the Python counterpart of
[DocumenterVitepress.jl](https://github.com/LuxDL/DocumenterVitepress.jl):

> `Sphinx : sphinx-vitepress :: Documenter.jl : DocumenterVitepress.jl`

```{toctree}
:caption: Guide
:hidden:

guide/getting-started
guide/configuration
guide/deploying
```

```{toctree}
:caption: Reference
:hidden:

reference/api
```

## Why

Sphinx has the best extraction and cross-referencing in any language ecosystem:
autodoc reads your code, napoleon understands NumPy and Google docstrings, and
intersphinx links a type in your signature to the page that documents it in
another project. What it has not had is a front end people enjoy reading.

VitePress supplies that — instant navigation, real search, dark mode — but knows
nothing about Python. This builder is the join between them.

## What you keep

Everything on the read side of Sphinx is untouched, because extensions like
autodoc and MyST produce a document tree long before any builder runs:

- `conf.py`, unchanged apart from optional `vitepress_*` settings
- autodoc, autosummary, napoleon, MyST, and most third-party extensions
- intersphinx in both directions — your site publishes an `objects.inv`
- other Sphinx builders: `make latexpdf` still works from the same sources
