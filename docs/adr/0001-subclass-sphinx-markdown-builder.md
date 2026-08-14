# ADR 0001: Subclass sphinx-markdown-builder instead of vendoring or rewriting

**Status:** accepted (2026-08-14)

## Decision

Depend on `sphinx-markdown-builder>=0.6.10,<0.7` (MIT, Liran Funaro) and
subclass its `MarkdownBuilder`/`MarkdownTranslator`, overriding only where
VitePress markdown diverges from GitHub markdown.

## Rationale

- Its translator already covers the docutils/autodoc node long tail (tables,
  field lists, `desc*` signatures, footnotes) with a graceful warn-once
  fallback. That is a large amount of work we do not need to repeat.
- Its internals are NOT a declared stable API, hence the tight `<0.7` pin.

## Fallback

If subclassing turns brittle across upstream releases, vendor
`translator.py`, `contexts.py`, and `escape.py` into
`sphinx_vitepress/_vendor/`, retaining the MIT headers and updating
NOTICE.md (including the doctree2md BSD-2 ancestry).
