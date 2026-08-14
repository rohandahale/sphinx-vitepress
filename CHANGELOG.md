# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-08-14

### Added

- `vitepress_source_url` gives every documented object a *source* badge
  linking to the exact lines that define it, for example
  `.../src/pkg/core.py#L42-L57`. Set it to everything up to the
  repository-relative path:

      vitepress_source_url = "https://github.com/you/project/blob/main"

  Pin a commit instead of a branch if the links should keep pointing at
  the code each version was built from. The file path is worked out
  relative to the git working tree, so it matches your repository layout
  without further configuration. This configures `sphinx.ext.linkcode`
  for you; a `linkcode_resolve` you define yourself still wins.

### Changed

- Source badges are always visible. They previously appeared only on
  hover, which read as a missing feature and never showed at all on touch
  devices.

### Fixed

- `prune_virtual_page_links` and `write_inventory` were missing
  docstrings, so `automodule` skipped them and they were absent from the
  rendered API reference.

## [0.1.3] - 2026-08-14

A review of the whole repository turned up several ways the package could
lose content or break a user's site. Everything below is fixed and covered
by tests.

### Fixed

- Pruning Sphinx's stock "Indices and tables" links no longer takes real
  content with it. A page whose only content was that block was written as
  an empty file, its title gone while the sidebar still linked to it, and
  unrelated headings with no body yet were deleted from other pages.
- `sphinx-vitepress init` followed by a build now works on a clean
  install. The scaffolded project loads MyST, which was only a development
  dependency, so the documented quickstart failed with an extension error.
- `sphinx-vitepress init` no longer overwrites an existing `index.md`. It
  refuses when either `conf.py` or `index.md` is already present.
- Copying the bundled theme into `<sourcedir>/.vitepress/theme/`, the
  documented way to customize it, produced a site that would not build:
  the generated `accent.css` was written only for the bundled theme while
  the copied entry point still imported it.
- `sphinx-vitepress deploy` can no longer damage a published tree. Version
  folders are built to a staging directory and swapped in only on success,
  so a failed build cannot delete a live version; `--devurl` must be a
  single path segment, since it was joined onto the deploy directory and
  then removed; and releasing an older line no longer moves `stable` back
  onto it.
- Toctree entries `self`, `genindex`, `modindex` and `search` no longer
  become sidebar links to pages that are never generated. VitePress does
  not check links inside the generated config, so these shipped silently.
- The published `objects.inv` no longer advertises those same pages, which
  handed other projects cross-references that 404.
- A `code-block` whose classes are exactly `code` no longer crashes the
  build with `IndexError`.
- A failed `npm install` reports what went wrong instead of a traceback,
  and dependencies are reinstalled when `package.json` changes, so
  upgrading no longer keeps building against the previous VitePress pin.

### Changed

- `docutils` and `myst-parser` are declared as runtime dependencies rather
  than relied on transitively.
- Python 3.14 is tested and declared as supported.
- The navbar shows at most six top-level entries; this is now documented
  rather than silently dropping the rest. The sidebar is unaffected.

## [0.1.2] - 2026-08-14

### Changed

- Third-party notices moved from `NOTICE.md` into `LICENSE`, so a single
  file carries the licence and the attributions it requires.
- The README covers installation and basic use; configuration, deployment
  and the API reference live in the documentation rather than being
  duplicated.
- The reference page is called "API" instead of "Python API".

### Fixed

- The project description shown on PyPI no longer claims the package is
  unpublished.

## [0.1.1] - 2026-08-14

### Changed

- Shortened the package summary to "A Sphinx builder that renders your
  documentation with VitePress."

## [0.1.0] - 2026-08-14

First release. A Sphinx builder that renders documentation with VitePress.

### Added

- **`vitepress` builder**: `sphinx-build -b vitepress <src> <out>` emits
  VitePress-flavored Markdown, a generated `.vitepress/config.mts`,
  `package.json` and a theme. Registered through an entry point, so it works
  without editing `extensions`.
- **VitePress markdown dialect**: `:::` containers for every docutils
  admonition, explicit `{#id}` heading anchors, `$$` math, code-fence language
  remapping, and `<abbr>` support.
- **Vue-safe output**: VitePress compiles pages as Vue templates, so `<`/`>`
  become entities, `{{` is neutralized, mustaches inside inline code are
  wrapped in `<span v-pre>`, and `raw:: html` blocks are shielded (configurable
  via `vitepress_raw_html`).
- **API rendering**: autodoc objects become collapsible `<details>` cards with
  an anchored binding, a type badge, and a fenced signature. A *source* badge is
  added when `sphinx.ext.linkcode` is configured. `vitepress_docstring_style =
  "headings"` restores plain headings.
- **Navigation**: sidebar and nav generated from the toctree, with `:caption:`
  becoming a collapsible sidebar group and a nav dropdown. Inline toctree lists
  (duplicated by the sidebar) are dropped unless `vitepress_inline_toctree` is
  set.
- **Cross-references both ways**: intersphinx resolves outward as usual, and
  the site publishes an `objects.inv` at its root so other Sphinx projects can
  link into it.
- **Theme**: ported from DocumenterVitepress.jl, with accent palettes selected
  by `vitepress_accent`: presets sampled from matplotlib colormaps (`blue`,
  `afmhot`, `viridis`, `plasma`, `inferno`, `magma`, `cividis`, `ocean`), a
  single color, four explicit stops, or per-mode palettes.
- **Hero landing pages**: `vitepress_frontmatter` sets per-page VitePress
  frontmatter, including `layout: home`.
- **Site chrome**: GitHub icon and per-page edit links from `vitepress_repo`
  (the repository-relative docs path is derived from the git working tree);
  footer copyright from Sphinx's own `copyright`; logo and favicon from
  `html_logo`/`html_favicon`.
- **CLI**: `sphinx-vitepress init | dev | build | deploy`. `build --no-build`
  stops after markdown and config, requiring no Node.
- **Versioned deploys**: `sphinx-vitepress deploy` builds one complete site per
  version alias (`--keep breaking|minor|patch`), writes `versions.js` and a root
  redirect, and keeps previously deployed versions working. A navbar version
  picker ships with the theme.

### Notes

- Sphinx's stock *Indices and tables* block links to `genindex`/`modindex`/
  `search`, which only the HTML builders create. Those links are removed, along
  with any section they empty, so VitePress's dead-link check stays enabled.
- Targets VitePress 1.6.x.

[Unreleased]: https://github.com/rohandahale/sphinx-vitepress/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.4
[0.1.3]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.3
[0.1.2]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.2
[0.1.1]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.1
[0.1.0]: https://github.com/rohandahale/sphinx-vitepress/releases/tag/v0.1.0
