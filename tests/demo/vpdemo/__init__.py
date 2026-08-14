"""vpdemo — a tiny astronomy-flavored package for testing sphinx-vitepress.

Its docstrings are deliberately hostile to VitePress: they contain Vue
mustaches, angle brackets, math, doctests, tables, and every napoleon section
we care about.
"""

from vpdemo.core import SIGMA_SB, CatalogEntry, Simulation, blackbody_flux

__all__ = ["SIGMA_SB", "CatalogEntry", "Simulation", "blackbody_flux"]
__version__ = "0.1.0"
