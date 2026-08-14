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

import posixpath
from typing import TYPE_CHECKING

from docutils import nodes
from sphinx_markdown_builder.contexts import (
    SubContext,
    SubContextParams,
    TableContext,
    TitleContext,
    WrappedContext,
)
from sphinx_markdown_builder.escape import escape_html_quote, escape_markdown_chars
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

#: Pages the Sphinx HTML builders synthesize but that have no VitePress
#: equivalent (its built-in local search replaces them). Nearly every
#: Sphinx project's index page links to these, and VitePress fails builds
#: on dead links, so the links are emitted as plain text instead.
#: Genuinely broken links are left alone, since VitePress *should* catch those.
VIRTUAL_PAGES = frozenset({"genindex", "modindex", "py-modindex", "search"})


def _is_source_link(reference: nodes.Element) -> bool:
    """Whether a reference is the ``[source]`` link on a signature.

    Both linkcode and viewcode mark their link's text with the
    ``viewcode-link`` class, which is what distinguishes it from the
    intersphinx-resolved type annotations that also appear in signatures.
    """
    return any(
        "viewcode-link" in inline.get("classes", []) for inline in reference.findall(nodes.inline)
    )


def _find_source_url(signature: nodes.Element) -> str | None:
    """URL of the ``[source]`` link Sphinx attached to a signature, if any.

    ``linkcode`` emits an absolute repository URL; ``viewcode`` emits a
    relative link into its generated ``_modules`` pages, which this builder
    does not produce, so only absolute links are used.
    """
    for reference in signature.findall(nodes.reference):
        if not _is_source_link(reference):
            continue
        uri = reference.get("refuri", "")
        if uri and "://" in uri:
            return str(uri)
    return None


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
        self._docstring_style: str = self.config.vitepress_docstring_style
        self._desc_first_sig: list[bool] = []
        self._sig_ids: list[str] = []
        self._sig_name: str | None = None
        self._sig_source_url: str | None = None
        self._in_signature = False

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

    @pushing_context
    def visit_reference(self, node: nodes.Element) -> None:
        if self._in_signature and _is_source_link(node):
            # Already rendered as the summary's "source" badge; letting it
            # through would print a literal [source] inside the signature.
            raise nodes.SkipNode
        if self._in_signature or self._is_virtual_page_ref(node):
            # Signatures land inside a code fence: a markdown link would show
            # as literal [name](url) noise, so render just the text.
            # (Intersphinx-linked type annotations trigger this.)
            self._push_context(SubContext())
            return
        super().visit_reference(node)

    def _is_virtual_page_ref(self, node: nodes.Element) -> bool:
        if not node.get("internal", self.status.default_ref_internal):
            return False
        uri = node.get("refuri", "")
        if not uri or "://" in uri:
            return False
        target = posixpath.basename(uri.split("#")[0])
        suffix = self.config.markdown_uri_doc_suffix
        if suffix and target.endswith(suffix):
            target = target[: -len(suffix)]
        return target in VIRTUAL_PAGES

    @pushing_context
    def visit_abbreviation(self, node: nodes.Element) -> None:
        explanation = node.get("explanation")
        if explanation:
            self._push_context(
                WrappedContext(f'<abbr title="{escape_html_quote(explanation)}">', "</abbr>")
            )
        else:
            self._push_context(SubContext())

    def visit_compound(self, node: nodes.Element) -> None:
        # Sphinx renders a toctree inline as a nested link list. VitePress
        # already shows exactly those links in its sidebar, so repeating
        # them in the body is duplication, and on a `layout: home` page it
        # buries the hero under a wall of links. Opt back in with
        # vitepress_inline_toctree = True.
        if self.config.vitepress_inline_toctree:
            return
        if "toctree-wrapper" in node.get("classes", []):
            raise nodes.SkipNode

    @pushing_context
    def visit_field_name(self, _node: nodes.Element) -> None:
        self._push_context(WrappedContext("**", ":**"))

    @pushing_context
    def visit_field_body(self, node: nodes.Element) -> None:
        # Start the body on the SAME line as the field name, since a line
        # break there loses the separating space and renders as
        # "Parameters:temperature". A body that is itself a list must keep
        # its own line, or its first bullet is swallowed into the heading.
        starts_with_list = any(
            isinstance(child, (nodes.bullet_list, nodes.enumerated_list))
            for child in node.children[:1]
        )
        if starts_with_list:
            self._push_context(SubContext(SubContextParams(1, 1)))
        else:
            # The separating space belongs to the body, so a body that does
            # start on its own line leaves no trailing space behind.
            self._push_context(SubContext(SubContextParams(0, 1)))
            self.add(" ")

    @pushing_context
    def visit_literal_emphasis(self, _node: nodes.Element) -> None:
        # napoleon splits type annotations like dict[str, int] into MANY
        # adjacent literal_emphasis nodes; italicizing each one produces
        # `*dict* *[**str*...` which markdown-it renders as literal-asterisk
        # soup. Plain text is correct and matches how the types read.
        self._push_context(SubContext())

    @pushing_context
    def visit_desc_annotation(self, _node: nodes.Element) -> None:
        # Signature annotations ("class ", "property ", "= default") end up
        # inside a fenced code signature, where italic markers would show as
        # raw asterisks. Emit them plain.
        self._push_context(SubContext())

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

    # -- API objects -> <details> docstring blocks (DocumenterVitepress style) --
    #
    # vitepress_docstring_style = "details" (default) wraps every autodoc
    # object in `<details class="docstring custom-block" open>` with a
    # <summary> holding the anchored binding name plus a <Badge> for the
    # object type, followed by the full signature in a python fence: the
    # DocumenterVitepress.jl look. "headings" keeps plain ###-level headings.

    def visit_desc(self, node: nodes.Element) -> None:
        self._push_status(desc_type=node.attributes.get("desctype", ""))
        if self._docstring_style == "details":
            self.add('<details class="docstring custom-block" open>', prefix_eol=2, suffix_eol=1)
            self._desc_first_sig.append(True)

    def depart_desc(self, _node: nodes.Element) -> None:
        if self._docstring_style == "details":
            self._desc_first_sig.pop()
            self.add("</details>", prefix_eol=2, suffix_eol=2)
        self._pop_status()

    def visit_desc_signature(self, node: nodes.Element) -> None:
        """API object signature: always anchored so cross-references resolve."""
        if self._docstring_style != "details":
            for anchor in node.get("ids", []):
                self._add_anchor(anchor)
            h_level = 4 if node.get("class", None) else 3
            self._push_context(TitleContext(h_level))
            return
        self._sig_ids = list(node.get("ids", []))
        self._sig_name = str(node.get("fullname", "")) or None
        self._sig_source_url = _find_source_url(node)
        # Capture the signature text raw (it lands inside a code fence).
        self._in_signature = True
        self._push_status(escape_text=False)
        self._push_context(SubContext())

    def depart_desc_signature(self, _node: nodes.Element) -> None:
        if self._docstring_style != "details":
            self._pop_context()
            return
        signature_ctx = self._ctx_queue.pop()
        signature = signature_ctx.make().strip()
        self._pop_status()
        self._in_signature = False
        self._emit_signature(signature)

    def _source_link(self) -> str:
        """A "source" badge linking into the repository, DV-style.

        ``sphinx.ext.linkcode`` (and ``viewcode`` with a repo configured)
        attach the resolved URL to the signature node; without either
        extension there is simply no badge.
        """
        url = self._sig_source_url
        if not url:
            return ""
        return (
            f'<Badge class="source-link" type="info">'
            f'<a href="{escape_html_quote(url)}" target="_blank" rel="noreferrer">source</a>'
            f"</Badge>"
        )

    def _emit_signature(self, signature: str) -> None:
        ids = self._sig_ids
        anchor = ids[0] if ids else ""
        name = self._sig_name or signature.split("(")[0].strip()
        if self._desc_first_sig and self._desc_first_sig[-1]:
            # First signature of this object: it becomes the <summary>.
            self._desc_first_sig[-1] = False
            badge = escape_html_quote(self.status.desc_type or "object")
            if anchor:
                quoted = escape_html_quote(anchor)
                opener, closer = f'<a id="{quoted}" href="#{quoted}">', "</a>"
            else:
                opener = closer = ""
            self.add(
                f'<summary>{opener}<span class="docstring-binding">{escape_vue(name)}</span>'
                f'{closer} <Badge type="info" text="{badge}" />{self._source_link()}</summary>',
                prefix_eol=1,
                suffix_eol=2,
            )
            extra_ids = ids[1:]
        else:
            extra_ids = ids
        for extra in extra_ids:
            self._add_anchor(extra)
        self.add(f"```python\n{signature}\n```", prefix_eol=2, suffix_eol=2)

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
        classes = node["classes"]
        # `.. code-block:: :class: code` yields exactly ["code"], so the
        # second entry cannot be assumed to exist.
        language = classes[1] if "code" in classes and len(classes) > 1 else ""
        if "language" in node:
            language = node["language"]
        language = FENCE_LANGUAGE_REMAP.get(language, language)
        self.add(f"```{language}", prefix_eol=1, suffix_eol=1)

    def visit_doctest_block(self, _node: nodes.Element) -> None:
        self._push_status(escape_text=False)
        language = FENCE_LANGUAGE_REMAP.get("pycon", "pycon")
        self.add(f"```{language}", prefix_eol=1, suffix_eol=1)
