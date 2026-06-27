"""Maintained Python interface for spherical-harmonic transforms.

The :mod:`pyspharm` package is the forward-looking API of the
``pyspharm-ng`` distribution.  The historical :mod:`spharm` import remains
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

try:
    __version__ = version("pyspharm-ng")
except PackageNotFoundError:  # Running from an unpacked source tree.
    __version__ = "0.1.0.dev0"

__all__ = [
    "GridConfiguration",
    "PrecisionError",
    "SphericalHarmonicTransform",
    "as_complex64",
    "as_real32",
    "__version__",
]
