"""Typed, explicit facade over the compatibility :mod:`spharm` engine.

This module deliberately delegates numerical work to ``spharm.Spharmt``.  It
adds a maintained public vocabulary, input validation and explicit precision
handling without duplicating or changing SPHEREPACK algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from numbers import Integral, Real
from typing import Any, Literal, Optional, Tuple

import numpy as np

from spharm import Spharmt

GridType = Literal["regular", "gaussian"]
LegendreMode = Literal["stored", "computed"]


class PrecisionError(TypeError):
    """Raised when an input does not use the single-precision legacy ABI."""


@dataclass(frozen=True)
class GridConfiguration:
    """Immutable description of a spherical grid and transform configuration.

    Parameters
    ----------
    nlon, nlat
        Longitude and latitude counts. Fields use shape ``(nlat, nlon)`` or
        ``(nlat, nlon, nt)``.
    radius
        Sphere radius in metres.
    grid
        ``"regular"`` for equally spaced latitudes or ``"gaussian"`` for
        Gaussian latitudes.
    legendre
        ``"stored"`` precomputes associated Legendre functions; ``"computed"``
        uses less memory and recomputes them for each operation.
    """

    nlon: int
    nlat: int
    radius: float = 6.3712e6
    grid: GridType = "regular"
    legendre: LegendreMode = "stored"

    def __post_init__(self) -> None:
        _validate_positive_integer(self.nlon, "nlon", minimum=4)
        _validate_positive_integer(self.nlat, "nlat", minimum=3)
        if not isinstance(self.radius, Real) or isinstance(self.radius, bool):
            raise TypeError("radius must be a real number")
        if not np.isfinite(self.radius) or self.radius <= 0.0:
            raise ValueError("radius must be finite and greater than zero")
        if self.grid not in {"regular", "gaussian"}:
            raise ValueError("grid must be either 'regular' or 'gaussian'")
        if self.legendre not in {"stored", "computed"}:
            raise ValueError("legendre must be either 'stored' or 'computed'")


class SphericalHarmonicTransform:
    """Modern public interface for scalar and wind spherical harmonics.

    The underlying SPHEREPACK/F2PY ABI is single precision. Transform methods
    therefore require ``numpy.float32`` real fields and ``numpy.complex64``
    spectral coefficients. Use :func:`as_real32` and :func:`as_complex64` to
    make a conversion explicit at an application boundary.
    """

    def __init__(
        self,
        nlon: int,
        nlat: int,
        *,
        radius: float = 6.3712e6,
        grid: GridType = "regular",
        legendre: LegendreMode = "stored",
    ) -> None:
        self._configuration = GridConfiguration(
            nlon=nlon,
            nlat=nlat,
            radius=float(radius),
            grid=grid,
            legendre=legendre,
        )
        self._legacy = Spharmt(
            self._configuration.nlon,
            self._configuration.nlat,
            rsphere=self._configuration.radius,
            gridtype=self._configuration.grid,
            legfunc=self._configuration.legendre,
        )

    @property
    def configuration(self) -> GridConfiguration:
        """Return the immutable configuration used by this transform."""

        return self._configuration

    @property
    def nlon(self) -> int:
        """Number of longitudes."""

        return self._configuration.nlon

    @property
    def nlat(self) -> int:
        """Number of latitudes."""

        return self._configuration.nlat

    @property
    def radius(self) -> float:
        """Sphere radius in metres."""

        return self._configuration.radius

    @property
    def grid(self) -> GridType:
        """Latitude grid family."""

        return self._configuration.grid

    @property
    def legendre(self) -> LegendreMode:
        """Associated-Legendre-function storage mode."""

        return self._configuration.legendre

    def analyze_scalar(
        self, field: np.ndarray, *, truncation: Optional[int] = None
    ) -> np.ndarray:
        """Analyze a scalar field into triangular spectral coefficients.

        ``field`` must have shape ``(nlat, nlon)`` or ``(nlat, nlon, nt)`` and
        dtype ``float32``. The returned coefficients have dtype ``complex64``.
        """

        native_field = self._real_field(field, name="field")
        ntrunc = self._validate_truncation(truncation)
        result = self._legacy.grdtospec(native_field, ntrunc=ntrunc)
        return np.asfortranarray(result, dtype=np.complex64)

    def synthesize_scalar(self, coefficients: np.ndarray) -> np.ndarray:
        """Synthesize a scalar field from triangular spectral coefficients.

        ``coefficients`` must have shape ``(ncoeff,)`` or ``(ncoeff, nt)`` and
        dtype ``complex64``. The returned field has dtype ``float32``.
        """

        native_coefficients = self._spectral_coefficients(
            coefficients, name="coefficients"
        )
        result = self._legacy.spectogrd(native_coefficients)
        return np.asfortranarray(result, dtype=np.float32)

    def analyze_wind(
        self,
        zonal_wind: np.ndarray,
        meridional_wind: np.ndarray,
        *,
        truncation: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Analyze zonal/meridional wind into vorticity/divergence coefficients.

        Both inputs use the same shape and dtype rules as :meth:`analyze_scalar`.
        The returned tuple is ``(vorticity, divergence)`` in ``complex64``.
        """

        u = self._real_field(zonal_wind, name="zonal_wind")
        v = self._real_field(meridional_wind, name="meridional_wind")
        if u.shape != v.shape:
            raise ValueError("zonal_wind and meridional_wind must have the same shape")
        ntrunc = self._validate_truncation(truncation)
        vorticity, divergence = self._legacy.getvrtdivspec(u, v, ntrunc=ntrunc)
        return (
            np.asfortranarray(vorticity, dtype=np.complex64),
            np.asfortranarray(divergence, dtype=np.complex64),
        )

    def synthesize_wind(
        self, vorticity: np.ndarray, divergence: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Synthesize zonal/meridional wind from vorticity/divergence spectra."""

        vrt = self._spectral_coefficients(vorticity, name="vorticity")
        div = self._spectral_coefficients(divergence, name="divergence")
        if vrt.shape != div.shape:
            raise ValueError("vorticity and divergence must have the same shape")
        zonal_wind, meridional_wind = self._legacy.getuv(vrt, div)
        return (
            np.asfortranarray(zonal_wind, dtype=np.float32),
            np.asfortranarray(meridional_wind, dtype=np.float32),
        )

    def _real_field(self, values: np.ndarray, *, name: str) -> np.ndarray:
        array = _require_dtype(values, np.float32, name=name)
        if array.ndim not in {2, 3}:
            raise ValueError(f"{name} must have rank 2 or 3, got rank {array.ndim}")
        if array.shape[:2] != (self.nlat, self.nlon):
            raise ValueError(
                f"{name} must start with shape ({self.nlat}, {self.nlon}), "
                f"got {array.shape}"
            )
        _require_finite(array, name=name)
        return np.asfortranarray(array)

    def _spectral_coefficients(self, values: np.ndarray, *, name: str) -> np.ndarray:
        array = _require_dtype(values, np.complex64, name=name)
        if array.ndim not in {1, 2}:
            raise ValueError(f"{name} must have rank 1 or 2, got rank {array.ndim}")
        truncation = _truncation_from_coefficient_count(array.shape[0])
        if truncation > self.nlat - 1:
            raise ValueError(
                f"{name} encodes truncation {truncation}, which exceeds "
                f"the maximum {self.nlat - 1} for this transform"
            )
        _require_finite(array, name=name)
        return np.asfortranarray(array)

    def _validate_truncation(self, truncation: Optional[int]) -> int:
        if truncation is None:
            return self.nlat - 1
        _validate_positive_integer(truncation, "truncation", minimum=0)
        if truncation > self.nlat - 1:
            raise ValueError(
                f"truncation must be at most {self.nlat - 1}, got {truncation}"
            )
        return int(truncation)


def as_real32(values: Any) -> np.ndarray:
    """Explicitly convert a real array-like value to finite Fortran ``float32``.

    This is the recommended conversion boundary before calling the modern API.
    Integer and floating input are accepted; complex values are rejected.
    """

    array = np.asarray(values)
    if np.iscomplexobj(array) or not np.issubdtype(array.dtype, np.number):
        raise TypeError("values must be a real numeric array-like object")
    converted = np.asfortranarray(array, dtype=np.float32)
    _require_finite(converted, name="values")
    return converted


def as_complex64(values: Any) -> np.ndarray:
    """Explicitly convert a numeric array-like value to finite Fortran ``complex64``."""

    array = np.asarray(values)
    if not np.issubdtype(array.dtype, np.number):
        raise TypeError("values must be a numeric array-like object")
    converted = np.asfortranarray(array, dtype=np.complex64)
    _require_finite(converted, name="values")
    return converted


def _validate_positive_integer(value: Any, name: str, *, minimum: int) -> None:
    if not isinstance(value, Integral) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}, got {value}")


def _require_dtype(values: Any, dtype: np.dtype, *, name: str) -> np.ndarray:
    array = np.asarray(values)
    expected = np.dtype(dtype)
    if array.dtype != expected:
        converter = "as_real32" if expected == np.dtype(np.float32) else "as_complex64"
        raise PrecisionError(
            f"{name} must have dtype {expected.name}; use "
            f"{converter}(...) to convert explicitly"
        )
    return array


def _require_finite(values: np.ndarray, *, name: str) -> None:
    if not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must not contain NaN or infinity")


def _truncation_from_coefficient_count(count: int) -> int:
    if count < 1:
        raise ValueError("spectral coefficient arrays must not be empty")
    discriminant = 1 + 8 * int(count)
    root = isqrt(discriminant)
    if root * root != discriminant or (root - 3) % 2:
        raise ValueError(
            "spectral coefficient count must equal "
            "(truncation + 1) * (truncation + 2) // 2"
        )
    truncation = (root - 3) // 2
    if truncation < 0:
        raise ValueError("spectral coefficient count is not triangular")
    return truncation
