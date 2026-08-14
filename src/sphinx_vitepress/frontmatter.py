"""Per-page VitePress frontmatter.

VitePress reads a YAML block at the top of each page; the important use is
``layout: home``, which turns a page into the hero/features landing page.

The block is emitted as JSON, which is valid YAML (a flow mapping), so no
YAML emitter is needed and no escaping bugs are possible — VitePress's
frontmatter parser accepts it.
"""

from __future__ import annotations

import json
from typing import Any


def render(data: dict[str, Any]) -> str:
    """Render a frontmatter block, or ``""`` when there is nothing to emit."""
    if not data:
        return ""
    body = json.dumps(data, indent=2, ensure_ascii=False)
    return f"---\n{body}\n---\n\n"
