from __future__ import annotations

from sphinx_vitepress.escape import escape_vue


def test_angle_brackets_become_entities() -> None:
    assert escape_vue("dict[str, int] and a < b > c") == "dict[str, int] and a &lt; b &gt; c"


def test_mustaches_become_numeric_entities() -> None:
    assert escape_vue("{{ name }}") == "&#123;&#123; name }}"


def test_component_like_text_is_neutralized() -> None:
    assert escape_vue("<Response>") == "&lt;Response&gt;"


def test_ampersand_is_left_alone() -> None:
    # DocumenterVitepress.jl precedent: & survives so search JSON stays readable.
    assert escape_vue("R&D") == "R&D"


def test_plain_text_untouched() -> None:
    assert escape_vue("nothing special here") == "nothing special here"
