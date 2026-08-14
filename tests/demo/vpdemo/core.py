"""Core routines for the vpdemo package."""

from __future__ import annotations

import math
from dataclasses import dataclass

SIGMA_SB = 5.670374419e-8
"""Stefan-Boltzmann constant in W m^-2 K^-4."""


def blackbody_flux(temperature: float) -> float:
    r"""Total emitted flux of a blackbody.

    Implements the Stefan-Boltzmann law,

    .. math::

        F = \sigma T^4,

    where :math:`\sigma` is the Stefan-Boltzmann constant.

    Parameters
    ----------
    temperature : float
        Effective temperature in kelvin. Must satisfy ``temperature > 0``
        (note the comparison: 0 < temperature).

    Returns
    -------
    float
        Emitted flux in W m^-2.

    Raises
    ------
    ValueError
        If ``temperature`` is not positive.

    Examples
    --------
    >>> round(blackbody_flux(5772.0) / 1e7, 2)
    6.29

    Notes
    -----
    Pipeline config templates like ``{{ output_dir }}`` are common in the
    wild; this sentence and the literal {{ placeholder }} exist to stress
    the Vue-safety of the generated markdown.
    """
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    return SIGMA_SB * temperature**4


def brightness_temperature(flux_jy: float, frequency_hz: float, solid_angle_sr: float) -> float:
    """Rayleigh-Jeans brightness temperature of a resolved source.

    Several parameters, so the field body renders as a list — the case that
    regressed once when field names and bodies were put on one line.

    Parameters
    ----------
    flux_jy : float
        Flux density in jansky.
    frequency_hz : float
        Observing frequency in hertz.
    solid_angle_sr : float
        Source solid angle in steradian.

    Returns
    -------
    float
        Brightness temperature in kelvin.
    """
    k_b = 1.380649e-23
    intensity = flux_jy * 1e-26 / solid_angle_sr
    return intensity * (299792458.0 / frequency_hz) ** 2 / (2 * k_b)


@dataclass
class CatalogEntry:
    """A single source in a catalog.

    Attributes
    ----------
    name : str
        Source identifier, e.g. ``"M87*"``.
    flux_jy : float
        Flux density in jansky.
    """

    name: str
    flux_jy: float


class Simulation:
    """Toy radiative simulation.

    Parameters
    ----------
    grid : dict[str, int]
        Mapping of axis name to number of cells, e.g. ``{"x": 128}``.

    Warnings
    --------
    Results for grids with fewer than 8 cells per axis are unreliable.
    """

    def __init__(self, grid: dict[str, int]) -> None:
        self.grid = dict(grid)

    @property
    def n_cells(self) -> int:
        """Total number of cells across all axes."""
        return math.prod(self.grid.values()) if self.grid else 0

    def run(self, steps: int = 10) -> list[float]:
        """Run the simulation.

        Parameters
        ----------
        steps : int, optional
            Number of time steps, by default 10.

        Returns
        -------
        list of float
            Mean intensity per step.
        """
        return [float(i) / max(steps, 1) for i in range(steps)]
