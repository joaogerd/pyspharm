"""Compatibility package for the historical :mod:`spharm` public API."""

from importlib.metadata import PackageNotFoundError, version

from . import spharm as _legacy_module
from .spharm import *
from .spharm import __doc__

try:
    __version__ = version("pyspharm-ng")
except PackageNotFoundError:  # Running from an unpacked source tree.
    __version__ = "0.2.0"

_legacy_module.__version__ = __version__
del _legacy_module
