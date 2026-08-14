"""Vue-safe escaping for VitePress markdown output.

VitePress compiles every markdown page as a Vue template, so three things in
plain prose are hazards that classic markdown escaping does not cover:

- ``<`` / ``>`` — start HTML/component tags; ``dict[str, int]`` is safe but
  ``Callable<T>``-style text or a stray ``<Response>`` is a build error.
- ``{{`` — starts a Vue interpolation; ``{{ placeholder }}`` text either
  errors or silently evaluates.
- Fenced code blocks are auto-``v-pre`` by VitePress and need no treatment;
  inline code is handled separately by the translator (wrapped in
  ``<span v-pre>`` only when it contains ``{{``).

Following DocumenterVitepress.jl's writer (writer.jl ~L1144), ``&`` is
deliberately NOT escaped: VitePress copies heading text verbatim into per-page
search JSON, and double-escaping there reads worse than the rare literal
``&lt;`` a user may type.
"""

from __future__ import annotations


def escape_vue(text: str) -> str:
    """Escape text so Vue's template compiler treats it as plain prose."""
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    # Numeric entities survive markdown-it untouched and never re-form a
    # mustache in the compiled template.
    return text.replace("{{", "&#123;&#123;")
