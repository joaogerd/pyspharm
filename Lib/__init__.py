"""Compatibility package for the historical :mod:`spharm` public API."""

from .spharm import *
from .spharm import __doc__

# The distribution is versioned independently from the legacy implementation.
# Keep the historical import path stable while the modern pyspharm API is built.
__version__ = "0.1.0.dev0"
