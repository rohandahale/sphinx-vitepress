# sphinx-vitepress — Design Document

**Status:** approved 2026-08-14 · pre-code
**Goal:** the Python equivalent of [DocumenterVitepress.jl](https://github.com/LuxDL/DocumenterVitepress.jl) — Sphinx-grade documentation power (autodoc, napoleon/NumPy docstrings, intersphinx, MyST Markdown authoring, PDF via LaTeX) rendered through VitePress's modern UI.
**Visual target:** https://luxdl.github.io/DocumenterVitepress.jl/stable/

**Provenance note:** the initial research for this project came from a Gemini chat that fabricated its two key packages (`sphinx-vitepress`, `sphinx-notes-vitepress` — both 404 on PyPI's JSON API, verified 2026-08-14). Everything below was rebuilt from primary sources, fetched and verified on 2026-08-14. Claims that could not be verified are marked UNVERIFIED.

## Decisions

- **Scope:** reusable open-source package, eventually published to PyPI.
- **Architecture:** Sphinx engine + custom VitePress **builder** — the structural mirror of DocumenterVitepress.jl (`Sphinx : sphinx-vitepress :: Documenter.jl : DocumenterVitepress.jl`).
- **Dogfood target:** bundled demo package (`demo/vpdemo`) with deliberately tricky docstrings.
- **Name:** `sphinx-vitepress` (import `sphinx_vitepress`) — unclaimed, conventional for a Sphinx extension. Re-check availability at publish time.
- **License:** MIT (ours). All ports from MIT/BSD sources recorded in NOTICE.md.

## Verified ground truth

- `sphinx-vitepress`, `sphinx-notes-vitepress`: do not exist (PyPI JSON API 404).
- [sphinx-markdown-builder](https://github.com/liran-funaro/sphinx-markdown-builder) v0.6.10, MIT, maintained — working Sphinx→Markdown builder to subclass.
- DocumenterVitepress.jl — Markdown writer backend for Documenter.jl; local reference copy at `DocumenterVitepress.jl-0.3.5/`.
- [Sail's docs](https://docs.lakesail.com/sail/main/development/documentation/) — production Sphinx→VitePress bridge (Sphinx renders HTML fragments to JSON; VitePress ingests at build time). Validates the hybrid; not reusable.
- VitePress: npm `latest = 1.6.4`, `next = 2.0.0-alpha.19` (2026-08-02); v2 requires Node ≥ 22.
- [mkdocstrings-python](https://mkdocstrings.github.io/python/usage/) reads + publishes `objects.inv` outside Sphinx — prior art if a non-Sphinx mode is ever added.
- [Read the Docs hosts VitePress officially](https://docs.readthedocs.com/platform/stable/intro/vitepress.html).

---

## A) sphinx-markdown-builder anatomy

**License / attribution.** MIT, "Copyright (c) 2023-2026, Liran Funaro" ([LICENSE](https://raw.githubusercontent.com/liran-funaro/sphinx-markdown-builder/main/LICENSE)). Lineage: forked from clayrisser/sphinx-markdown-builder (MIT, Clay Risser), originally based on `doctree2md` from nb2plots by Matthew Brett (BSD-2). Depending on it as a library: no obligations beyond normal packaging. Vendoring/deriving code: retain the MIT copyright notice (and note the BSD-2 ancestry) in LICENSE/NOTICE. v0.6.10, `requires-python >=3.7`, deps `sphinx>=5.1.0, tabulate, docutils`.

**Structure** (6 modules in [`sphinx_markdown_builder/`](https://github.com/liran-funaro/sphinx-markdown-builder/tree/main/sphinx_markdown_builder)):

- `builder.py` — `MarkdownBuilder(sphinx.builders.Builder)`: `name="markdown"`, `format="markdown"`, `default_translator_class=MarkdownTranslator`, `allow_parallel=True`; `write_doc` writes `visitor.astext()` via `docutils.io.StringOutput`; `get_outdated_docs` compares mtimes; `get_target_uri` returns `f"{docname}{markdown_uri_doc_suffix}"`; `finish()` copies download files.
- `writer.py` — thin `docutils.writers.Writer` running `document.walkabout(visitor)`.
- `translator.py` (28 KB) — the meat: all `visit_*`/`depart_*` methods.
- `contexts.py` — stack of `SubContext`/`IndentContext`/`TableContext`/`WrappedContext` objects the translator pushes/pops.
- `escape.py` — CommonMark character escaping.

**Registration.** `setup(app)` calls `app.add_builder(MarkdownBuilder)` + 8 `app.add_config_value("markdown_*", ...)`, returns `{"version", "parallel_read_safe": True, "parallel_write_safe": True}`. Also exposes entry point `[project.entry-points."sphinx.builders"] markdown = "sphinx_markdown_builder"` so `sphinx-build -M markdown` works without listing it in `extensions` — Sphinx's `registry.preload_builder` reads `entry_points(group='sphinx.builders')` ([sphinx/registry.py](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/registry.py) ~L173-180).

**Node coverage.** Declarative `PREDEFINED_ELEMENTS` dict (node name → push-context/SKIP/ignore; skips `index`, `autosummary_toc`, `substitution_definition`, …) plus explicit `visit_*` for: all admonitions (rendered as quote-boxes via `_push_box` — **zero `:::` container support today**), images, paragraphs, line blocks, definition lists, math/math_block, literal/literal_block/doctest_block, block quotes, sections/titles/rubrics, references/targets/downloads, bullet/enumerated lists, the full autodoc `desc*` family (signatures, parameters, returns, field lists), `versionmodified`, tables (via `tabulate`), footnotes. `unknown_visit` warns once per node type then `SkipNode` — graceful degradation worth keeping.

**Gaps we fill:** VitePress containers, `{#id}` anchors, Vue-safe escaping, frontmatter, sidebar/config generation, theme, build orchestration, versioned deploy.

## B) DocumenterVitepress.jl specifics worth mirroring

Local copy: `DocumenterVitepress.jl-0.3.5/`. MIT, (c) 2023 LuxDL — CSS/theme/Vue components portable with attribution. Source map: `src/writer.jl` (markdown emission, 67 KB), `src/vitepress_config.jl` (config generation), `src/frontmatter.jl` (YAML merge), `src/DocumenterVitepress.jl` (deploy/versions), `src/ANSIBlocks.jl`, `src/extension_hooks.jl`, `template/`, `ext/DocumenterVitepressDocumenterCitationsExt.jl` (third-party-extension precedent).

**Markdown it emits** (`src/writer.jl`):
- Admonitions → `::: tip|warning|danger|caution Title … :::` with `note`→`tip`, unknown categories→`tip`+title.
- Headings with explicit anchors: `## Heading {#id}` (ids sanitized by stripping `[]()*`).
- Math as `$...$` / `$$...$$`.
- Text escaping of **only** `<`/`>` → `&lt;`/`&gt;` (deliberately not `&`, because VitePress copies titles verbatim into per-page JSON — writer.jl ~L1144-1148).
- Docstrings as `<details class='jldocstring custom-block' open><summary><a id='…'><span class="jlbinding">Name</span></a> <Badge type="info" text="Function"/></summary>…</details>` with a `<Badge class="source-link">` source link (~L620-660).
- Tabs via `vitepress-plugin-tabs`; footnotes via `markdown-it-footnote`; fence-language remap (`julia-repl`→`julia`, `documenter-ansi`→`ansi`).
- Per-page merged YAML frontmatter (single block, escaped scalars — `frontmatter.jl`).
- Interactive HTML output wrapped in `<ClientOnly>` + custom `v-exec-scripts` directive; light/dark image MIME variants.
- Writes a Sphinx-compatible `objects.inv` (`write_inventory=true`).

**Config/sidebar generation** (`src/vitepress_config.jl`): ships a template `config.mts` full of `REPLACE_ME_DOCUMENTER_VITEPRESS` placeholders, then string-replaces: `base` (deploy path + version base), `outDir`, serialized `sidebar`/`nav` from the pages tree (groups get `collapsed`), `title`, `description`, `editLink` pattern, GitHub `socialLinks`, `logo` (auto-detected `assets/logo.png` → `public/`), favicon, and a `noindex` meta for non-stable builds. User-supplied `docs/src/.vitepress/{config.mts,theme/*}` override the template.

**Template/theme** (`template/src/.vitepress/`): `config.mts` sets `cleanUrls: true`, `lastUpdated`, shiki `github-light/dark`, local search `{provider:'local', options:{detailedView:true}}`, markdown-it plugins (tabs, footnote, custom `mathjax-plugin.ts`, `julia-repl-transformer.ts`), injects `versions.js` + `siteinfo.js` into `head`. `theme/index.ts` extends `DefaultTheme`, registers `VersionPicker.vue` (reads `window.DOC_VERSIONS` / `DOCUMENTER_CURRENT_VERSION`; adapted from Makie.jl, MIT), `AuthorBadge`, `Authors`, `SidebarDrawerToggle`, nolebase enhanced-readabilities; CSS: `style.css` (8.8 KB) + `docstrings.css` + `overrides.css`.

**Versioned deployment** (`src/DocumenterVitepress.jl` ~L79-163): `determine_bases(subfolder; keep=:breaking)` expands a tag (e.g. `v1.2.3`) into base aliases (`v1`, `stable`, per `keep ∈ :patch/:minor/:breaking`); for each base *i*, rewrite `base:`/`outDir` and run a **full VitePress build per base** into `build/1`, `build/2`, …, appending the base name to `build/bases.txt`; each build gets `siteinfo.js` (`var DOCUMENTER_CURRENT_VERSION = "…"`). `deploydocs(repo=…)` reads `bases.txt` and pushes each folder to `gh-pages/<base>`; post-push scan of root folders' `siteinfo.js` regenerates root `versions.js` (`var DOC_VERSIONS=[...]`, `DOCUMENTER_NEWEST`, `DOCUMENTER_STABLE`) plus a root `index.html` meta-refresh redirect to `stable`/`dev`.

**Node toolchain.** DV vendors Node via Julia's `NodeJS_20_jll` artifact; runs `npm install` + `npm run env -- vitepress build`; substitutes a default `package.json` (pins `vitepress ^1.6.4`) if the user has none. **Windows: automated builds disabled** — warns to run manually with system Node ≥ 22.11 (writer.jl ~L390-440).

**Weak points to beat:** raw `{{ }}` in prose is NOT escaped (we will v-pre it); Windows automated builds disabled (we keep Windows CI); vendored Node is a Julia-artifact luxury PyPI can't cheaply replicate (we document system Node instead).

**API surface (parity checklist):** `MarkdownVitepress(repo; devbranch, devurl="dev", deploy_url, description, build_vitepress=true, install_npm=true, md_output_path=".documenter", deploy_decision, assets, inventory_version, sidebar_drawer=false, write_inventory=true, noindex_non_stable=true, keep=:breaking, ansicolor=true)`; `generate_template(dir, pkg)`; `deploydocs(repo, target="build", dirname)`.

## C) VitePress target specifics

- **Versions (verified 2026-08-14):** npm dist-tags `latest = 1.6.4`, `next = 2.0.0-alpha.19` ([registry](https://registry.npmjs.org/-/package/vitepress/dist-tags); [releases](https://github.com/vuejs/vitepress/releases)). Target **1.6.x** as the default pin; CI-track the 2-alpha.
- **Node:** current (v2) docs require Node ≥ 22 ([getting started](https://vitepress.dev/guide/getting-started)). v1.6's exact minimum: UNVERIFIED (DV runs it on vendored Node 20).
- **Config** ([site config](https://vitepress.dev/reference/site-config)): `<srcdir>/.vitepress/config.{js,ts,mjs,mts}` default-exporting `defineConfig({...})`; `base` must start and end with `/`; `srcDir`, `outDir` (default `./.vitepress/dist`), `cleanUrls`; **dead links fail the build by default** — `ignoreDeadLinks: true | 'localhostLinks' | [patterns]`. `themeConfig`: `nav`, nested `sidebar` (`{text, link, items, collapsed}`), `socialLinks`, `editLink`, `footer`, `outline`, `search: {provider:'local'}`.
- **Markdown extensions** ([markdown guide](https://vitepress.dev/guide/markdown)): containers `::: info|tip|warning|danger|details` with trailing custom title; GitHub alerts `> [!NOTE]`; line highlighting ` ```py{1,4,6-8} ` and `// [!code highlight]`; code groups (`::: code-group` + ` ```py [label] `); `[[toc]]`; emoji; custom header anchors `{#id}`; math requires `npm add markdown-it-mathjax3` + `markdown: { math: true }`.
- **Linking** ([routing](https://vitepress.dev/guide/routing)): omit extensions in inter-page links; `foo.md` → `/foo` under cleanUrls.
- **Vue gotchas** ([using Vue](https://vitepress.dev/guide/using-vue)): `{{ }}` in prose/tables and malformed/unknown raw HTML are compiled as Vue templates — **build errors**; fenced code blocks are auto-wrapped in `v-pre` (inline code treatment: UNVERIFIED — escape defensively); escape hatches are `<span v-pre>` and the `::: v-pre` container. `<`/`>` in generated prose (type hints like `dict[str, int]`!) must be entity-escaped. Unknown shiki fence languages warn and fall back to plaintext (UNVERIFIED exact behavior).

## D) Sphinx builder integration essentials

- **Packaging/registration:** ordinary extension — `setup(app)` calls `app.add_builder(VitepressBuilder)` and returns `{"version", "parallel_read_safe": True, "parallel_write_safe": True}` ([app API](https://www.sphinx-doc.org/en/master/extdev/appapi.html)). Also register entry point `[project.entry-points."sphinx.builders"] vitepress = "sphinx_vitepress"` so `sphinx-build -b vitepress` works without `extensions` edits.
- **Doctree source:** the write phase (`Builder.write_documents → _write_serial/_write_parallel`) calls `env.get_and_resolve_doctree(docname, builder=self)` and hands the result to `write_doc(docname, doctree)` ([builders/__init__.py](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/builders/__init__.py) ~L750-828; [builder API](https://www.sphinx-doc.org/en/master/extdev/builderapi.html)). Post-transforms (reference resolution included) are already applied.
- **Intersphinx:** hooks the `missing-reference` event ([intersphinx source](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/ext/intersphinx/__init__.py)); by write time, unresolved `pending_xref`s have become plain `reference` nodes with absolute external `refuri` — `visit_reference` needs zero intersphinx awareness. **Inbound direction:** only the HTML builder writes `objects.inv` natively, so we emit our own via `sphinx.util.inventory.InventoryFile.dump` ([inventory.py](https://github.com/sphinx-doc/sphinx/blob/master/sphinx/util/inventory.py)), with roles from `env.domaindata` (`py:*`, `std:doc`, `std:label`).
- **Sidebar from toctree:** `env.toctree_includes: dict[docname, list[docname]]` + `env.titles[docname]` + `config.root_doc` → build the nested VitePress `sidebar`/`nav` in `finish()` without re-walking doctrees.
- **MyST/napoleon/autodoc:** read-side extensions producing standard doctrees before any builder runs — zero work for us; users keep their existing `conf.py`.

## E) Package layout (src layout, uv + hatchling, ruff, pytest, Python ≥ 3.11)

**Key decision:** depend on `sphinx-markdown-builder>=0.6.10,<0.7` (its internals are not a stable API) and **subclass** `MarkdownBuilder`/`MarkdownTranslator`. Fallback if subclassing gets brittle: vendor `translator.py`/`contexts.py`/`escape.py` into `sphinx_vitepress/_vendor/` retaining MIT headers + NOTICE entries (incl. doctree2md BSD-2 lineage).

```
sphinx-vitepress/
├── pyproject.toml                    # hatchling; entry-points: "sphinx.builders" vitepress=…;
│                                     #   console script sphinx-vitepress = sphinx_vitepress.cli:main
├── LICENSE  NOTICE.md
├── src/sphinx_vitepress/
│   ├── __init__.py                   # setup(app): add_builder + vitepress_* config values
│   ├── builder.py                    # VitepressBuilder(MarkdownBuilder): name="vitepress";
│   │                                 #   write_doc adds frontmatter; finish(): sidebar → config.mts
│   │                                 #   → theme copy → public/ assets → objects.inv → optional npx build
│   ├── translator.py                 # VitepressTranslator(MarkdownTranslator): ::: admonitions,
│   │                                 #   {#id} headings, desc_* → <details><summary> docstring blocks,
│   │                                 #   math $$, tables w/ escaping, fence-language remap
│   ├── escape.py                     # Vue-safe text escaping: <,> → entities; {{ → <span v-pre>;
│   │                                 #   never applied inside fences
│   ├── sidebar.py                    # env.toctree_includes + titles → sidebar/nav JSON
│   ├── config_writer.py              # render template config.mts (placeholder replacement, DV-style)
│   ├── frontmatter.py                # merged single YAML block per page
│   ├── inventory.py                  # objects.inv via sphinx.util.inventory.InventoryFile.dump
│   ├── nodejs.py                     # find node/npm (version-check), npm install / npx vitepress build|dev
│   ├── versions.py                   # determine_bases(keep), bases.txt, siteinfo.js, versions.js regen
│   ├── deploy.py                     # versioned gh-pages layout writer (CLI + Actions)
│   ├── cli.py                        # sphinx-vitepress init|dev|build|deploy (argparse)
│   └── template/                     # package-data: package.json, src/.vitepress/config.mts
│                                     #   (placeholders), theme/{index.ts,style.css,docstrings.css},
│                                     #   components/VersionPicker.vue
├── demo/vpdemo/                      # bundled dogfood pkg: typed napoleon docstrings, MyST pages,
│                                     #   math, admonitions, tables, intersphinx refs, tricky {{ }} content
├── docs/                             # dogfooded once M5 lands (conf.py uses sphinx_vitepress)
├── tests/                            # golden-file tests (Sphinx source → expected .md);
│                                     #   config/sidebar units; vitepress-build smoke (skipped w/o node)
└── .github/workflows/{ci.yml, docs.yml}
```

## F) Milestones

- **M0 Scaffold:** pyproject + src layout, uv, ruff, pytest, mypy, CI matrix (3.11–3.13 × ubuntu/macos/windows), ADRs (subclass-vs-vendor; VitePress 1.6 pin), placeholder PyPI release to claim the name.
- **M1 Minimal builder:** `VitepressBuilder`/`VitepressTranslator` subclasses; Vue-safe escaping; `:::` admonitions (incl. `note`→`tip`, `seealso`→`info`); `{#id}` heading anchors; fence-language remap (`pycon`→`python`, `ipython`→`python`, `default`→txt); demo package builds; hand-written `.vitepress/config.mts`; `npx vitepress build` green **with strict dead links**; golden-file tests.
- **M2 Config + CLI:** sidebar/nav from `toctree_includes`; `config_writer` placeholders (base, title, description, editLink, socialLinks, logo/favicon → `public/`, local search); frontmatter merge; extensionless `get_target_uri`; `sphinx-vitepress init` (template copier à la `generate_template`), `dev` (sphinx build + `vitepress dev`), `build`.
- **M3 Theme parity:** port `style.css`/`docstrings.css` + theme `index.ts` (attribute in NOTICE); autodoc `desc*` nodes → `<details class='docstring custom-block'><summary>…<Badge/></summary>` with source links; math via `markdown: {math: true}` + markdown-it-mathjax3; code-groups for MyST tabs (stretch); screenshot-diff against https://luxdl.github.io/DocumenterVitepress.jl/stable/.
- **M4 Intersphinx + versioned deploy:** emit `objects.inv` (roles: `py:*`, `std:doc`, `std:label` from `env.domaindata`); round-trip test (a second Sphinx project resolves refs INTO our built site; our site resolves refs OUT to docs.python.org); `versions.py` (bases.txt, siteinfo.js, versions.js, root redirect) + `VersionPicker.vue`; reusable GitHub Actions deploy workflow + PR-preview cleanup (mirror DV's `DocPreviewCleanup.yml`).
- **M5 Dogfood + 0.1.0:** `docs/` built by sphinx-vitepress itself, versioned on GitHub Pages; migration guide ("furo → VitePress"); compat matrix (Sphinx 7/8 × VitePress 1.6/2-alpha); Windows verified; PyPI release + announcement.

## G) Risk register

| Risk | Mitigation |
|---|---|
| **Docutils node long tail** (sphinx-design, nbsphinx, domains emit exotic nodes) | Inherit warn-once `unknown_visit` + skip; `PREDEFINED_ELEMENTS`-style override table; golden tests per popular extension; documented HTML-passthrough fallback |
| **Vue interpolation breakage** (`{{ }}` in docstrings/tables/prose) | Central `escape.py`: `{{` → `<span v-pre>`, `<`/`>` → entities (DV precedent, writer.jl ~L1144); fences auto-safe; fuzz corpus of Jinja/C++/JS docstrings in the demo package |
| **Raw HTML compiled as Vue → build errors** | Wrap `raw:: html` in `v-pre` by default; config `vitepress_raw_html = "v-pre"|"passthrough"|"drop"`; DV's `<ClientOnly>` pattern for script-bearing output |
| **Dead-link build failures** on generated anchors/index-style pages | Deterministic self-emitted `{#id}` anchors; suppress genindex-style stub pages; `ignoreDeadLinks` config passthrough; CI keeps strict mode on the demo |
| **Local-search quality** on huge API pages | `search.options.detailedView`; per-object page splitting via frontmatter titles; document Algolia DocSearch option |
| **Node toolchain friction** | Markdown + config always emitted without Node; shell-outs only from the CLI; `--no-build` escape hatch (mirrors `build_vitepress=false`); evaluate a `nodeenv`-based `[node]` extra (UNVERIFIED fit) vs plain "install Node ≥ 22" docs |
| **Windows support** (DV disables automated builds there) | `posixpath` for URIs; list-args `subprocess` (no shell); `npm.cmd` resolution; Windows CI from M0 |
| **Upstream drift** (sphinx-markdown-builder internals; VitePress v2 config changes) | Pin `<0.7` + documented vendor fallback; keep generated config compatible with 1.6 and 2-alpha (CI job on `vitepress@next`) |
