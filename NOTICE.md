# NOTICE

sphinx-vitepress is MIT-licensed (see [LICENSE](LICENSE)). It builds on, and plans to
port code and assets from, the MIT/BSD projects below. Entries marked *(pending)*
apply once the corresponding code or assets are actually ported — update this ledger
in the same commit as any port.

- **sphinx-markdown-builder** — MIT, Copyright (c) 2023–2026 Liran Funaro
  (<https://github.com/liran-funaro/sphinx-markdown-builder>). Used as a library
  dependency (subclassed); *(pending)* vendored translator modules if subclassing is
  ever replaced by vendoring. Ancestry: forked from clayrisser/sphinx-markdown-builder
  (MIT, Clay Risser), originally based on `doctree2md` from nb2plots
  (BSD-2-Clause, Matthew Brett).
- **DocumenterVitepress.jl** — MIT, Copyright (c) 2023 LuxDL contributors
  (<https://github.com/LuxDL/DocumenterVitepress.jl>). **Ported** (adapted):
  theme CSS (`src/sphinx_vitepress/template/theme/style.css` and
  `docstrings.css` derive from its `template/src/.vitepress/theme/` files),
  theme `index.ts` structure, the placeholder-substitution config.mts pattern,
  and the `<details>` docstring block markup emitted by our translator.
  *(pending)* the versioned-deploy design (`bases.txt`/`siteinfo.js`/
  `versions.js`) and `VersionPicker.vue`.
- **Makie.jl** — MIT (<https://github.com/MakieOrg/Makie.jl>). *(pending)*
  `VersionPicker.vue`, via DocumenterVitepress.jl.
- **VitePress** — MIT, Copyright (c) 2019–present Evan You and VitePress contributors
  (<https://github.com/vuejs/vitepress>). Runtime dependency installed via npm,
  not vendored.
