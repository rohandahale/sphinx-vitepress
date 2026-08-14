"""VitePress-flavored markdown translator.

Subclasses sphinx-markdown-builder's ``MarkdownTranslator`` (MIT, Liran
Funaro) and overrides emission where VitePress markdown diverges from plain
GitHub markdown: admonitions become ``:::`` containers, text is Vue-safe
escaped, headings carry explicit ``{#id}`` anchors, raw HTML is fenced off
from Vue, and code-fence languages unknown to shiki are remapped.

The behavioral reference is DocumenterVitepress.jl's ``src/writer.jl``
(local copy in the repo root); the rules are documented in DESIGN.md §B/§C.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docutils import nodes
from sphinx_markdown_builder.contexts import (
    SubContext,
    SubContextParams,
    TableContext,
    TitleContext,
)
from sphinx_markdown_builder.escape import escape_markdown_chars
from sphinx_markdown_builder.translator import (
    MarkdownTranslator,
    pushing_context,
    pushing_status,
)

from sphinx_vitepress.escape import escape_vue

if TYPE_CHECKING:
    from sphinx_vitepress.builder import VitepressBuilder

#: Sphinx/docutils admonition name -> (VitePress container kind, title).
#: VitePress kinds are limited to: info | tip | warning | danger | details.
ADMONITIONS: dict[str, tuple[str, str]] = {
    "note": ("tip", "Note"),
    "tip": ("tip", "Tip"),
    "hint": ("tip", "Hint"),
    "important": ("warning", "Important"),
    "attention": ("warning", "Attention"),
    "caution": ("warning", "Caution"),
    "warning": ("warning", "Warning"),
    "danger": ("danger", "Danger"),
    "error": ("danger", "Error"),
    "seealso": ("info", "See also"),
}

#: Fence languages shiki does not bundle -> safe replacements.
FENCE_LANGUAGE_REMAP: dict[str, str] = {
    "default": "python",
    "ipython": "python",
    "ipython3": "python",
    "python3": "python",
    "pycon": "python",
    "none": "",
    "text": "",
}

_VERSIONMODIFIED_KINDS: dict[str, str] = {
    "versionadded": "tip",
    "versionchanged": "info",
    "deprecated": "warning",
}


class ContainerContext(SubContext):
    """Collects a body and wraps it in a VitePress ``::: kind Title`` container."""

    def __init__(self, kind: str, title: str = "") -> None:
        super().__init__(SubContextParams(2, 2))
        self.kind = kind
        self.title = title

    def make(self) -> str:
        opener = f"::: {self.kind} {escape_vue(self.title)}".rstrip()
        return f"{opener}\n{super().make().strip()}\n:::"


class MathBlockContext(SubContext):
    """Collects display math and emits a tight ``$$`` fence.

    MyST's math nodes can start with a newline; a blank line inside a ``$$``
    block breaks markdown-it-mathjax3's block parsing, so the body is trimmed.
    """

    def __init__(self) -> None:
        super().__init__(SubContextParams(2, 2))

    def make(self) -> str:
        return f"$$\n{super().make().strip()}\n$$"


class AnchoredTitleContext(TitleContext):
    """A heading carrying an explicit VitePress anchor: ``## Title {#id}``."""

    def __init__(self, level: int, anchor: str | None) -> None:
        super().__init__(level)
        self.anchor = anchor

    def make(self) -> str:
        content = super().make()
        if self.anchor:
            return f"{content} {{#{self.anchor}}}"
        return content


class VitepressTranslator(MarkdownTranslator):
    """Emit VitePress-flavored markdown instead of plain GitHub markdown."""

    def __init__(self, document: nodes.document, builder: VitepressBuilder) -> None:
        super().__init__(document, builder)
        self._admonition_title_pending = False
        self._vpre_literal = False

    # -- Vue-safe text ---------------------------------------------------------

    def visit_Text(self, node: nodes.Text) -> None:
        text = node.astext().replace("\r", "")
        if self.config.markdown_flavor == "github":
            text = text.replace("\n", " ")
        if self.status.escape_text:
            text = escape_vue(escape_markdown_chars(text))
        self.add(text)

    def visit_literal(self, node: nodes.Element) -> None:
        # Fenced blocks are auto-v-pre'd by VitePress; inline code is not.
        # A mustache inside inline code would be interpolated by Vue, so wrap
        # exactly those spans in <span v-pre>.
        self._push_status(escape_text=False)
        self._vpre_literal = "{{" in node.astext()
        self.add("<span v-pre>`" if self._vpre_literal else "`")

    def depart_literal(self, _node: nodes.Element) -> None:
        self.add("`</span>" if self._vpre_literal else "`")
        self._vpre_literal = False
        self._pop_status()

    def visit_raw(self, node: nodes.Element) -> None:
        fmt = str(node.get("format", "")).lower()
        if "html" in fmt.split():
            mode = self.config.vitepress_raw_html
            if mode != "drop":
                text = node.astext()
                if mode == "v-pre":
                    text = f"<div v-pre>\n{text}\n</div>"
                self.add(text, prefix_eol=2, suffix_eol=2)
        raise nodes.SkipNode

    # -- Admonitions -> ::: containers -----------------------------------------

    def _push_admonition(self, name: str) -> None:
        kind, title = ADMONITIONS[name]
        self._push_context(ContainerContext(kind, title))

    @pushing_context
    def visit_note(self, _node: nodes.Element) -> None:
        self._push_admonition("note")

    @pushing_context
    def visit_tip(self, _node: nodes.Element) -> None:
        self._push_admonition("tip")

    @pushing_context
    def visit_hint(self, _node: nodes.Element) -> None:
        self._push_admonition("hint")

    @pushing_context
    def visit_important(self, _node: nodes.Element) -> None:
        self._push_admonition("important")

    @pushing_context
    def visit_attention(self, _node: nodes.Element) -> None:
        self._push_admonition("attention")

    @pushing_context
    def visit_caution(self, _node: nodes.Element) -> None:
        self._push_admonition("caution")

    @pushing_context
    def visit_warning(self, _node: nodes.Element) -> None:
        self._push_admonition("warning")

    @pushing_context
    def visit_danger(self, _node: nodes.Element) -> None:
        self._push_admonition("danger")

    @pushing_context
    def visit_error(self, _node: nodes.Element) -> None:
        self._push_admonition("error")

    @pushing_context
    def visit_seealso(self, _node: nodes.Element) -> None:
        self._push_admonition("seealso")

    @pushing_context
    def visit_admonition(self, node: nodes.Element) -> None:
        """Generic ``.. admonition:: Custom Title`` -> info container."""
        title_node = node.next_node(nodes.title)
        title = title_node.astext() if title_node is not None else ""
        self._admonition_title_pending = title_node is not None
        self._push_context(ContainerContext("info", title))

    @pushing_context
    def visit_versionmodified(self, node: nodes.Element) -> None:
        kind = _VERSIONMODIFIED_KINDS.get(node.attributes.get("type", ""), "info")
        self._push_context(ContainerContext(kind))

    # -- Headings with explicit anchors ----------------------------------------

    @pushing_status
    def visit_section(self, node: nodes.Element) -> None:
        self.ensure_eol(2)
        # The first id becomes the heading's {#id}; any extra ids (explicit
        # `.. _label:` targets) still need <a> anchors so refs to them resolve.
        for anchor in node.get("ids", [])[1:]:
            self._add_anchor(anchor)
        self._push_status(section_level=self.status.section_level + 1)

    @pushing_context
    def visit_title(self, node: nodes.Element) -> None:
        if self._admonition_title_pending:
            # Consumed by visit_admonition as the container title.
            self._admonition_title_pending = False
            raise nodes.SkipNode
        if isinstance(self.ctx, TableContext):
            self._push_context(TitleContext(4))
            return
        anchor = None
        parent = node.parent
        if isinstance(parent, nodes.section):
            ids = parent.get("ids", [])
            if ids:
                anchor = ids[0]
        self._push_context(AnchoredTitleContext(self.status.section_level, anchor))

    @pushing_context
    def visit_desc_signature(self, node: nodes.Element) -> None:
        """API object signature: always anchored so cross-references resolve."""
        for anchor in node.get("ids", []):
            self._add_anchor(anchor)
        h_level = 4 if node.get("class", None) else 3
        self._push_context(TitleContext(h_level))

    # -- Math ------------------------------------------------------------------

    def visit_math_block(self, _node: nodes.Element) -> None:
        self._push_status(escape_text=False)
        self._push_context(MathBlockContext())

    def depart_math_block(self, _node: nodes.Element) -> None:
        self._pop_context()
        self._pop_status()

    # -- Code fences -----------------------------------------------------------

    def visit_literal_block(self, node: nodes.Element) -> None:
        self._push_status(escape_text=False)
        language = node["classes"][1] if "code" in node["classes"] else ""
        if "language" in node:
            language = node["language"]
        language = FENCE_LANGUAGE_REMAP.get(language, language)
        self.add(f"```{language}", prefix_eol=1, suffix_eol=1)

    def visit_doctest_block(self, _node: nodes.Element) -> None:
        self._push_status(escape_text=False)
        language = FENCE_LANGUAGE_REMAP.get("pycon", "pycon")
        self.add(f"```{language}", prefix_eol=1, suffix_eol=1)
