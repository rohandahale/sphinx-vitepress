# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-08-14

First release. A Sphinx builder that renders documentation with VitePress.

### Added

- **`vitepress` builder** — `sphinx-build -b vitepress <src> <out>` emits
  VitePress-flavored Markdown, a generated `.vitepress/config.mts`,
  `package.json` and a theme. Registered through an entry point, so it works
  without editing `extensions`.
- **VitePress markdown dialect** — `:::` containers for every docutils
  admonition, explicit `{#id}` heading anchors, `$$` math, code-fence language
  remapping, and `<abbr>` support.
- **Vue-safe output** — VitePress compiles pages as Vue templates, so `<`/`>`
  become entities, `{{` is neutralized, mustaches inside inline code are
  wrapped in `<span v-pre>`, and `raw:: html` blocks are shielded (configurable
  via `vitepress_raw_html`).
- **API rendering** — autodoc objects become collapsible `<details>` cards with
  an anchored binding, a type badge, and a fenced signature. A *source* badge is
  added when `sphinx.ext.linkcode` is configured. `vitepress_docstring_style =
  "headings"` restores plain headings.
- **Navigation** — sidebar and nav generated from the toctree, with `:caption:`
  becoming a collapsible sidebar group and a nav dropdown. Inline toctree lists
  (duplicated by the sidebar) are dropped unless `vitepress_inline_toctree` is
  set.
- **Cross-references both ways** — intersphinx resolves outward as usual, and
  the site publishes an `objects.inv` at its root so other Sphinx projects can
  link into it.
- **Theme** — ported from DocumenterVitepress.jl, with accent palettes selected
  by `vitepress_accent`: presets sampled from matplotlib colormaps (`blue`,
  `afmhot`, `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `ocean`), a
  single color, four explicit stops, or per-mode palettes.
- **Hero landing pages** — `vitepress_frontmatter` sets per-page VitePress
  frontmatter, including `layout: home`.
- **Site chrome** — GitHub icon and per-page edit links from `vitepress_repo`
  (the repository-relative docs path is derived from the git working tree);
  footer copyright from Sphinx's own `copyright`; logo and favicon from
  `html_logo`/`html_favicon`.
- **CLI** — `sphinx-vitepress init | dev | build | deploy`. `build --no-build`
  stops after markdown and config, requiring no Node.
- **Versioned deploys** — `sphinx-vitepress deploy` builds one complete site per
  version alias (`--keep breaking|minor|patch`), writes `versions.js` and a root
  redirect, and keeps previously deployed versions working. A navbar version
  picker ships with the theme.

### Notes

- Sphinx's stock *Indices and tables* block links to `genindex`/`modindex`/
  `search`, which only the HTML builders create. Those links are removed, along
  with any section they empty, so VitePress's dead-link check stays enabled.
- Targets VitePress 1.6.x; CI also builds against the 2.0 alpha.

[Unreleased]: https://github.com/rohandahale/sphinx-vitepress/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.0
