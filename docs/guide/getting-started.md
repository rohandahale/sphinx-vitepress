# Getting started

## Requirements

- Python ≥ 3.11
- Node.js 20 or newer, only to run VitePress itself. Markdown generation never
  needs Node, so documentation can be generated on machines without it and
  built elsewhere.

## Install

```bash
pip install sphinx-vitepress
```

## An existing Sphinx project

Add the extension to `conf.py`:

```python
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_vitepress",
]
```

Then preview the site:

```bash
sphinx-vitepress dev docs
```

That runs Sphinx with the `vitepress` builder, writes markdown plus a generated
`.vitepress/config.mts`, `package.json` and theme, installs the Node
dependencies on first use, and starts VitePress in watch mode.

:::tip
The extension entry is optional. `sphinx-vitepress` registers the builder
through an entry point, so `sphinx-build -b vitepress docs _site` works even
without touching `extensions`.
:::

## A new project

```bash
sphinx-vitepress init docs
sphinx-vitepress dev docs
```

`init` writes a minimal `conf.py` and `index.md` and refuses to overwrite an
existing `conf.py`.

## Building for production

```bash
sphinx-vitepress build docs _site
```

The finished site lands in `_site/.vitepress/dist`. Add `--no-build` to stop
after markdown and config generation, which needs no Node at all:

```bash
sphinx-vitepress build docs _site --no-build
```

## What gets generated

```
_site/
├── *.md                     # your pages, in VitePress markdown
├── package.json             # pins vitepress + markdown-it-mathjax3
├── public/
│   └── objects.inv          # so other projects can link into this site
└── .vitepress/
    ├── config.mts           # title, nav, sidebar, search, edit links
    └── theme/               # styles, docstring cards, version picker
```

Anything you place in `<sourcedir>/.vitepress/` overrides the generated
equivalent, so full customization never requires forking this package.

## Dead links

VitePress fails a production build on dead links, and that check is left on
deliberately, because it catches broken cross-references that Sphinx's HTML
builders would have rendered as silently dangling anchors.

The one exception is handled for you: Sphinx's stock *Indices and tables* block
points at `genindex`, `modindex` and `search`, pages only the HTML builders
create. Those links are removed (VitePress's own search replaces them) along
with any section they leave empty.
