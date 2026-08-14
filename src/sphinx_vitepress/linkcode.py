"""Link each documented object to the exact lines that define it.

``sphinx.ext.linkcode`` asks the project for a URL per object but leaves
the work of finding one to ``conf.py``, so most projects either copy the
same twenty lines of :mod:`inspect` handling or settle for linking to the
top of a module. Setting ``vitepress_source_url`` installs a resolver that
finds the object's file and line range and produces, for example::

    https://github.com/you/project/blob/main/src/pkg/core.py#L42-L57

The file path is taken relative to the git working tree the source lives
in, so it matches the repository layout without further configuration.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sphinx.util import logging

if TYPE_CHECKING:
    from collections.abc import Callable

    from sphinx.application import Sphinx
    from sphinx.config import Config

logger = logging.getLogger(__name__)


def _git_root(path: Path) -> Path | None:
    for candidate in [path, *path.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def _unwrap(obj: Any) -> Any:
    """Peel decorators, properties and descriptors down to real source."""
    for attribute in ("fget", "func", "__func__", "__wrapped__"):
        nested = getattr(obj, attribute, None)
        if nested is not None:
            return _unwrap(nested)
    return obj


def _locate(module_name: str, fullname: str) -> tuple[Path, int, int] | None:
    """File and line range for a documented object, or None if unknown."""
    try:
        module = importlib.import_module(module_name)
    except Exception as err:
        # A module that cannot be imported (optional dependency, side
        # effects) must cost a source link, not the whole build.
        logger.debug("sphinx-vitepress: cannot import %s for source links: %s", module_name, err)
        return None

    obj: Any = module
    for part in filter(None, fullname.split(".")):
        obj = getattr(obj, part, None)
        if obj is None:
            # An attribute with no runtime object of its own (a dataclass
            # field, say): fall back to the module itself.
            obj = module
            break
    obj = _unwrap(obj)

    try:
        source_file = inspect.getsourcefile(obj)
    except TypeError:
        source_file = None
    if source_file is None:
        return None

    try:
        lines, start = inspect.getsourcelines(obj)
    except (OSError, TypeError):
        return Path(source_file), 0, 0
    return Path(source_file), start, start + len(lines) - 1


def make_resolver(base_url: str) -> Callable[[str, dict[str, Any]], str | None]:
    """Build a ``linkcode_resolve`` for a URL prefix ending in a ref.

    Parameters
    ----------
    base_url : str
        Everything up to the repository-relative path, for example
        ``https://github.com/you/project/blob/main``. Pin a commit rather
        than a branch if the links should keep pointing at the code the
        documentation was built from.

    Returns
    -------
    callable
        A resolver suitable for ``linkcode_resolve`` in ``conf.py``.
    """
    prefix = base_url.rstrip("/")

    def resolve(domain: str, info: dict[str, Any]) -> str | None:
        if domain != "py" or not info.get("module"):
            return None
        located = _locate(info["module"], info.get("fullname", ""))
        if located is None:
            return None
        source_file, start, end = located

        root = _git_root(source_file.resolve())
        if root is None:
            return None
        try:
            relative = source_file.resolve().relative_to(root).as_posix()
        except ValueError:  # pragma: no cover - outside the working tree
            return None

        if start and end:
            return f"{prefix}/{relative}#L{start}-L{end}"
        return f"{prefix}/{relative}"

    return resolve


def install(app: Sphinx, config: Config) -> None:
    """Wire up linkcode when ``vitepress_source_url`` is configured.

    A ``linkcode_resolve`` the project defined itself always wins.
    """
    base_url = getattr(config, "vitepress_source_url", "")
    if not base_url:
        return
    app.setup_extension("sphinx.ext.linkcode")
    if getattr(config, "linkcode_resolve", None) is None:
        config.linkcode_resolve = make_resolver(base_url)
