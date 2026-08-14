# Configuration

Every setting is optional. Where Sphinx already has an equivalent (`copyright`,
`html_logo`, `html_favicon`) that value is used, so most projects need only
`vitepress_repo`.

## Site identity

| Setting | Default | Purpose |
| --- | --- | --- |
| `vitepress_title` | `project` | Site title in the navbar |
| `vitepress_description` | derived | Meta description |
| `vitepress_base` | `"/"` | Base path; must start and end with `/` |
| `vitepress_logo` | `html_logo` | Navbar logo, copied into `public/` |
| `vitepress_favicon` | `html_favicon` | Favicon, copied into `public/` |

## Repository links

```python
vitepress_repo = "https://github.com/you/project"
```

This adds the GitHub icon to the navbar and a per-page *Edit this page* link.
The repository-relative path of your docs directory is derived by locating it
inside the git working tree, so `docs/` projects need nothing further. Override
it when that guess is wrong:

| Setting | Default | Purpose |
| --- | --- | --- |
| `vitepress_edit_branch` | `"main"` | Branch the edit links target |
| `vitepress_edit_link_pattern` | derived | Full pattern, e.g. `https://…/edit/main/docs/:path` |
| `vitepress_footer_message` | none | HTML shown above the copyright |

## Accent palette

```python
vitepress_accent = "viridis"
```

Presets are sampled from the matplotlib colormaps of the same name, so a site
can match the figures inside it: `blue` (default), `afmhot`, `viridis`,
`plasma`, `inferno`, `magma`, `cividis`, `ocean`.

Any of these also work:

```python
vitepress_accent = "#0087d7"  # one color
vitepress_accent = ["#0060a8", "#0087d7", "#0c9ff4", "#5fd7ff"]  # deep→glow
vitepress_accent = {"light": "ocean", "dark": "afmhot"}  # per mode
```

Stops are used by role, not position: light mode draws link text from the
darkest stop so it stays readable on white, while dark mode uses the brighter
end. The result is written to `.vitepress/theme/accent.css`.

## Navigation

The sidebar mirrors your toctrees in full. A `:caption:` becomes a
collapsible sidebar group and a navbar dropdown.

The navbar shows at most the first six top-level entries, since a wider bar
wraps badly on smaller screens; the sidebar is unaffected and still lists
everything.

## Landing pages

`vitepress_frontmatter` maps a document name to VitePress frontmatter. The main
use is turning the index into a hero page:

```python
vitepress_frontmatter = {
    "index": {
        "layout": "home",
        "hero": {
            "name": "my-project",
            "text": "What it does",
            "tagline": "One sentence more.",
            "actions": [
                {"theme": "brand", "text": "Get started", "link": "/guide"},
            ],
        },
        "features": [
            {"title": "Fast", "details": "Because of reasons."},
        ],
    }
}
```

## API rendering

| Setting | Default | Purpose |
| --- | --- | --- |
| `vitepress_docstring_style` | `"details"` | `"details"` renders each object as a collapsible card with a type badge; `"headings"` uses plain headings |
| `vitepress_write_inventory` | `True` | Publish `objects.inv` at the site root |

### Source links

Point `vitepress_source_url` at your repository and every documented object
gets a *source* badge linking to the exact lines that define it:

```python
vitepress_source_url = "https://github.com/you/project/blob/main"
```

The value is everything up to the repository-relative path, so the ref is
yours to choose. Pin a commit rather than a branch if the links should keep
pointing at the code each version was built from:

```python
vitepress_source_url = f"https://github.com/you/project/blob/{commit_sha}"
```

The file path is worked out relative to the git working tree the source
lives in, so it matches your repository layout with no further setup, and
the line range comes from the object itself:
`.../src/pkg/core.py#L42-L57`.

This configures [`sphinx.ext.linkcode`](https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html)
for you. A `linkcode_resolve` you define yourself always takes precedence.

### An index of the API

Sphinx has no per-page object index, but
[`autosummary`](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html)
produces one, and its links resolve to the objects documented further down
the same page:

```rst
.. autosummary::

   mypkg.core.load
   mypkg.core.Simulation
```

## Content handling

| Setting | Default | Purpose |
| --- | --- | --- |
| `vitepress_inline_toctree` | `False` | Sphinx renders each toctree inline as a link list; VitePress already shows those links in the sidebar, so the inline copy is dropped. Set `True` to keep it |
| `vitepress_raw_html` | `"v-pre"` | How `.. raw:: html` blocks are emitted: `"v-pre"` shields them from Vue, `"passthrough"` lets Vue compile them, `"drop"` removes them |

:::warning Vue safety
VitePress compiles every page as a Vue template, so `{{ … }}` and stray angle
brackets in prose are build errors. All generated text is escaped for this
automatically, including mustaches inside inline code, which are wrapped in
`<span v-pre>`. Fenced code blocks are already safe.
:::
