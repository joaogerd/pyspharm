"""Equivalence and validation tests for maintained grid utilities."""

from __future__ import annotations

import numpy as np
import pytest

import pyspharm
import spharm


def _scalar_coefficients() -> np.ndarray:
    nlon, nlat, truncation = 64, 33, 21
    transform = pyspharm.SphericalHarmonicTransform(nlon, nlat, grid="regular")
    latitude = np.linspace(np.pi / 2.0, -np.pi / 2.0, nlat, dtype=np.float32)
    longitude = np.linspace(0.0, 2.0 * np.pi, nlon, endpoint=False, dtype=np.float32)
    lon, lat = np.meshgrid(longitude, latitude)
    field = pyspharm.as_real32(np.cos(lat) * np.sin(3.0 * lon))
    return transform.analyze_scalar(field, truncation=truncation)


def test_gaussian_latitudes_weights_match_legacy_helper():
    expected_latitude, expected_weights = spharm.gaussian_lats_wts(36)
    latitude, weights = pyspharm.gaussian_latitudes_weights(36)

    assert latitude.dtype == np.float64
    assert weights.dtype == np.float64
    np.testing.assert_allclose(latitude, expected_latitude, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(weights, expected_weights, rtol=0.0, atol=0.0)


def test_spectral_indices_match_legacy_helper():
    expected_m, expected_n = spharm.getspecindx(21)
    zonal_wavenumber, total_wavenumber = pyspharm.spectral_indices(21)

    assert zonal_wavenumber.dtype == np.int32
    assert total_wavenumber.dtype == np.int32
    np.testing.assert_array_equal(zonal_wavenumber, expected_m)
    np.testing.assert_array_equal(total_wavenumber, expected_n)


def test_geodesic_points_match_legacy_helper():
    expected_latitude, expected_longitude = spharm.getgeodesicpts(4)
    latitude, longitude = pyspharm.geodesic_points(4)

    assert latitude.dtype == np.float32
    assert longitude.dtype == np.float32
    np.testing.assert_allclose(latitude, expected_latitude, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(longitude, expected_longitude, rtol=0.0, atol=0.0)


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(-45.0, 0.0), (0.0, 90.0), (37.5, 270.0)],
)
def test_interpolate_scalar_matches_legacy_helper(latitude: float, longitude: float):
    coefficients = _scalar_coefficients()
    truncation = 21
    expected = spharm.specintrp(
        longitude,
        coefficients,
        spharm.legendre(latitude, truncation),
    )

    actual = pyspharm.interpolate_scalar(
        coefficients,
        latitude=latitude,
        longitude=longitude,
    )

    assert isinstance(actual, np.float32)
    np.testing.assert_allclose(actual, expected, rtol=2.0e-5, atol=2.0e-5)


def test_interpolate_scalar_rejects_incompatible_inputs():
    coefficients = _scalar_coefficients()

    with pytest.raises(pyspharm.PrecisionError, match="complex64"):
        pyspharm.interpolate_scalar(
            coefficients.astype(np.complex128), latitude=0.0, longitude=0.0
        )
    with pytest.raises(ValueError, match="one-dimensional"):
        pyspharm.interpolate_scalar(
            coefficients[:, None], latitude=0.0, longitude=0.0
        )
    with pytest.raises(ValueError, match="coefficient count"):
        pyspharm.interpolate_scalar(
            np.ones(2, dtype=np.complex64), latitude=0.0, longitude=0.0
        )
    with pytest.raises(ValueError, match="latitude"):
        pyspharm.interpolate_scalar(coefficients, latitude=90.1, longitude=0.0)
    with pytest.raises(ValueError, match="longitude"):
        pyspharm.interpolate_scalar(coefficients, latitude=0.0, longitude=np.inf)


@pytest.mark.parametrize(
    ("function", "value"),
    [
        (pyspharm.gaussian_latitudes_weights, 0),
        (pyspharm.spectral_indices, -1),
        (pyspharm.geodesic_points, 0),
    ],
)
def test_integer_utilities_validate_lower_bounds(function, value):
    with pytest.raises(ValueError):
        function(value)
