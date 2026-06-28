"""Maintained Python interface for spherical-harmonic transforms.

The :mod:`pyspharm` package is the forward-looking API of the
``pyspharm-ng`` distribution. The historical :mod:`spharm` import remains
available unchanged during the compatibility period.
"""

from importlib.metadata import PackageNotFoundError, version

from .api import (
    GridConfiguration,
    PrecisionError,
    SphericalHarmonicTransform,
    as_complex64,
    as_real32,
)
from .regrid import regrid_scalar
from .utilities import (
    gaussian_latitudes_weights,
    geodesic_points,
    interpolate_scalar,
    spectral_indices,
)

try:
    __version__ = version("pyspharm-ng")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = [
    "GridConfiguration",
    "PrecisionError",
    "SphericalHarmonicTransform",
    "as_complex64",
    "as_real32",
    "gaussian_latitudes_weights",
    "geodesic_points",
    "interpolate_scalar",
    "regrid_scalar",
    "spectral_indices",
    "__version__",
]
