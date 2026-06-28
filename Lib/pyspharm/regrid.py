"""Validated scalar regridding through the compatibility SPHEREPACK engine."""

from __future__ import annotations

from numbers import Integral
from typing import Optional

import numpy as np

from spharm import regrid as _legacy_regrid

from .api import PrecisionError, SphericalHarmonicTransform


def regrid_scalar(
    source: SphericalHarmonicTransform,
    destination: SphericalHarmonicTransform,
    field: np.ndarray,
    *,
    truncation: Optional[int] = None,
    smoothing: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Spectrally regrid a scalar field between two spherical grids.

    Parameters
    ----------
    source, destination
        Maintained transform instances describing the source and destination
        grids. Their radii must match because the operation represents the same
        scalar field on a sphere.
    field
        Source-grid field with dtype ``float32`` and shape ``(nlat, nlon)`` or
        ``(nlat, nlon, nt)``.
    truncation
        Optional triangular truncation. The default is the largest truncation
        supported by both grids.
    smoothing
        Optional ``float32`` one-dimensional array of length
        ``destination.nlat`` containing spectral smoothing factors by total
        wavenumber.

    Returns
    -------
    numpy.ndarray
        A Fortran-contiguous ``float32`` field on the destination grid.

    Notes
    -----
    The operation delegates to the historical ``spharm.regrid`` implementation.
    It introduces validation and a maintained public API without reimplementing
    the underlying SPHEREPACK algorithms.
    """

    if not isinstance(source, SphericalHarmonicTransform):
        raise TypeError("source must be a SphericalHarmonicTransform")
    if not isinstance(destination, SphericalHarmonicTransform):
        raise TypeError("destination must be a SphericalHarmonicTransform")
    if not np.isclose(source.radius, destination.radius, rtol=0.0, atol=0.0):
        raise ValueError("source and destination must use the same sphere radius")

    native_field = source._real_field(field, name="field")
    maximum_truncation = min(source.nlat, destination.nlat) - 1
    ntrunc = _validate_truncation(truncation, maximum_truncation)
    smooth = _validate_smoothing(smoothing, destination.nlat)

    kwargs: dict[str, object] = {"ntrunc": ntrunc}
    if smooth is not None:
        kwargs["smooth"] = smooth
    result = _legacy_regrid(source._legacy, destination._legacy, native_field, **kwargs)
    return np.asfortranarray(result, dtype=np.float32)


def _validate_truncation(truncation: Optional[int], maximum: int) -> int:
    if truncation is None:
        return maximum
    if not isinstance(truncation, Integral) or isinstance(truncation, bool):
        raise TypeError("truncation must be an integer")
    if truncation < 0 or truncation > maximum:
        raise ValueError(f"truncation must be between 0 and {maximum}, got {truncation}")
    return int(truncation)


def _validate_smoothing(
    smoothing: Optional[np.ndarray], destination_nlat: int
) -> Optional[np.ndarray]:
    if smoothing is None:
        return None
    values = np.asarray(smoothing)
    if values.dtype != np.float32:
        raise PrecisionError("smoothing must have dtype float32; use as_real32(...) to convert")
    if values.ndim != 1 or values.shape[0] != destination_nlat:
        raise ValueError(
            "smoothing must be one-dimensional with length "
            f"{destination_nlat}, got shape {values.shape}"
        )
    if not np.all(np.isfinite(values)):
        raise ValueError("smoothing must not contain NaN or infinity")
    return np.asfortranarray(values)
