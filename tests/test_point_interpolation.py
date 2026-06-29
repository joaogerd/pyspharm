"""Regression tests for ABI-preserving pointwise interpolation adapters."""

from __future__ import annotations

import numpy as np

from spharm import _spherepack


def _compact_index(zonal_degree: int, total_degree: int, truncation: int) -> int:
    """Return a zero-based compact triangular coefficient index."""

    offset = sum(truncation - zonal + 1 for zonal in range(zonal_degree))
    return offset + total_degree - zonal_degree


def test_getlegfunc_matches_low_degree_normalized_associated_legendre_values():
    """Check degree 0/1 values without relying on the replaced adapter."""

    for latitude in (np.float32(-60.0), np.float32(0.0), np.float32(37.5)):
        actual = _spherepack.getlegfunc(latitude, 1)
        latitude_radians = np.float32(np.pi / 180.0) * latitude
        expected = np.asarray(
            [
                np.sqrt(np.float32(0.5)),
                np.sqrt(np.float32(1.5)) * np.sin(latitude_radians),
                np.sqrt(np.float32(0.75)) * np.cos(latitude_radians),
            ],
            dtype=np.float32,
        )

        assert actual.dtype == np.float32
        assert actual.flags.f_contiguous
        np.testing.assert_allclose(actual, expected, rtol=2.0e-6, atol=2.0e-6)


def test_specintrp_matches_explicit_compact_spectral_sum():
    """Check the longitude synthesis against the documented compact ordering."""

    truncation = 2
    longitude = np.float32(0.73)
    coefficients = np.asarray(
        [
            1.0 + 2.0j,
            -0.5 + 0.25j,
            0.75 - 0.5j,
            2.0 - 1.0j,
            -1.5 + 0.125j,
            0.25 + 0.8j,
        ],
        dtype=np.complex64,
    )
    legendre = np.asarray([0.5, -0.3, 0.7, 1.1, -0.2, 0.4], dtype=np.float32)

    actual = _spherepack.specintrp(longitude, truncation, coefficients, legendre)

    expected = np.float32(0.0)
    for zonal_degree in range(truncation + 1):
        wave_sum = np.complex64(0.0)
        for total_degree in range(zonal_degree, truncation + 1):
            coefficient_index = _compact_index(zonal_degree, total_degree, truncation)
            wave_sum += coefficients[coefficient_index] * legendre[coefficient_index]

        if zonal_degree == 0:
            expected = np.float32(wave_sum.real)
        else:
            phase = np.float32(zonal_degree) * longitude
            expected += np.float32(2.0) * np.float32(wave_sum.real) * np.cos(phase)
            expected -= np.float32(2.0) * np.float32(wave_sum.imag) * np.sin(phase)

    assert isinstance(actual, np.float32)
    np.testing.assert_allclose(actual, expected, rtol=2.0e-6, atol=2.0e-6)


def test_specintrp_constant_mode_is_longitude_independent():
    """The degree-zero component must be independent of longitude."""

    coefficients = np.asarray([np.complex64(3.25 - 9.0j)], dtype=np.complex64)
    legendre = np.asarray([np.float32(0.5)], dtype=np.float32)

    west = _spherepack.specintrp(np.float32(-2.3), 0, coefficients, legendre)
    east = _spherepack.specintrp(np.float32(5.7), 0, coefficients, legendre)

    np.testing.assert_array_equal(west, np.float32(1.625))
    np.testing.assert_array_equal(east, west)
