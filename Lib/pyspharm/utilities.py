"""Grid metadata and pointwise diagnostics backed by the legacy engine.

This module exposes small, frequently used operations that historically lived
at module level in :mod:`spharm`. The numerical implementation remains in the
compatibility engine; this public facade defines names, units, validation and
output dtypes for the maintained :mod:`pyspharm` API.
"""

from __future__ import annotations

from numbers import Integral, Real
from typing import Any, Tuple

import numpy as np

from spharm import (
    gaussian_lats_wts as _legacy_gaussian_lats_wts,
    getgeodesicpts as _legacy_geodesic_points,
    getspecindx as _legacy_spectral_indices,
    legendre as _legacy_legendre,
    specintrp as _legacy_specintrp,
)

from .api import PrecisionError, _require_finite, _truncation_from_coefficient_count


def gaussian_latitudes_weights(nlat: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return Gaussian latitude coordinates and quadrature weights.

    Parameters
    ----------
    nlat
        Number of Gaussian latitudes. It must be a positive integer.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        ``(latitude, weights)`` as one-dimensional ``float64`` arrays. Latitude
        is expressed in degrees north and ordered north-to-south. The weights
        are the Gaussian quadrature weights associated with those latitudes.

    Notes
    -----
    Grid metadata is returned in double precision, matching the documented
    historical helper. This does not change the ``float32`` / ``complex64``
    ABI required by transform methods.
    """

    _require_integer(nlat, "nlat", minimum=1)
    latitude, weights = _legacy_gaussian_lats_wts(int(nlat))
    return (
        np.asfortranarray(latitude, dtype=np.float64),
        np.asfortranarray(weights, dtype=np.float64),
    )


def spectral_indices(truncation: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return triangular-storage indices for spectral coefficients.

    Parameters
    ----------
    truncation
        Triangular total-wavenumber limit.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        ``(zonal_wavenumber, total_wavenumber)`` as one-dimensional ``int32``
        arrays. Their entries align with the first dimension of the compact
        triangular ``complex64`` coefficient array used by the transform API.
    """

    _require_integer(truncation, "truncation", minimum=0)
    zonal_wavenumber, total_wavenumber = _legacy_spectral_indices(int(truncation))
    return (
        np.asfortranarray(zonal_wavenumber, dtype=np.int32),
        np.asfortranarray(total_wavenumber, dtype=np.int32),
    )


def geodesic_points(edge_points: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return points of an icosahedral spherical geodesic.

    Parameters
    ----------
    edge_points
        Number of points on the edge of one geodesic triangle. The returned
        point count is ``10 * (edge_points - 1) ** 2 + 2``.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        ``(latitude, longitude)`` as one-dimensional ``float32`` arrays in
        degrees. Longitudes use the historical ``[0, 360]`` convention.
    """

    _require_integer(edge_points, "edge_points", minimum=1)
    latitude, longitude = _legacy_geodesic_points(int(edge_points))
    return (
        np.asfortranarray(latitude, dtype=np.float32),
        np.asfortranarray(longitude, dtype=np.float32),
    )


def interpolate_scalar(
    coefficients: np.ndarray,
    *,
    latitude: float,
    longitude: float,
) -> np.float32:
    """Interpolate one scalar spectrum at a latitude/longitude point.

    Parameters
    ----------
    coefficients
        One-dimensional, compact triangular ``complex64`` coefficient array.
    latitude, longitude
        Point coordinates in degrees north and degrees east, respectively.

    Returns
    -------
    numpy.float32
        Interpolated scalar value.

    Notes
    -----
    This function computes associated Legendre values internally and delegates
    the point interpolation to the historical SPHEREPACK wrapper. It currently
    accepts one spectrum and one point per call; batch interpolation remains a
    separate future API increment.
    """

    spectrum = _require_complex64_vector(coefficients, name="coefficients")
    truncation = _truncation_from_coefficient_count(spectrum.size)
    latitude_degrees = _require_coordinate(latitude, "latitude", minimum=-90.0, maximum=90.0)
    longitude_degrees = _require_coordinate(longitude, "longitude")

    legendre_values = _legacy_legendre(latitude_degrees, truncation)
    result = _legacy_specintrp(longitude_degrees, spectrum, legendre_values)
    return np.float32(result)


def _require_integer(value: Any, name: str, *, minimum: int) -> None:
    if not isinstance(value, Integral) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")


def _require_coordinate(
    value: Any,
    name: str,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError(f"{name} must be a real number")
    coordinate = float(value)
    if not np.isfinite(coordinate):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and coordinate < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    if maximum is not None and coordinate > maximum:
        raise ValueError(f"{name} must be at most {maximum}")
    return coordinate


def _require_complex64_vector(values: Any, *, name: str) -> np.ndarray:
    array = np.asarray(values)
    if array.dtype != np.dtype(np.complex64):
        raise PrecisionError(
            f"{name} must have dtype complex64; use as_complex64(...) to convert explicitly"
        )
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional, got rank {array.ndim}")
    _require_finite(array, name=name)
    _truncation_from_coefficient_count(array.size)
    return np.asfortranarray(array)
