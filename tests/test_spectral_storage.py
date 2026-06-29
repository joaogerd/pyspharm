"""Regression tests for compact and expanded scalar spectral storage."""

from __future__ import annotations

import numpy as np

from spharm import _spherepack


def _compact_index(zonal_degree: int, total_degree: int, truncation: int) -> int:
    """Return the zero-based index in historical triangular storage."""

    offset = sum(truncation - zonal + 1 for zonal in range(zonal_degree))
    return offset + total_degree - zonal_degree


def _coefficients(truncation: int, nt: int) -> np.ndarray:
    """Build distinct single-precision compact values in Fortran order."""

    ncoefficients = (truncation + 1) * (truncation + 2) // 2
    real = np.arange(1, ncoefficients * nt + 1, dtype=np.float32).reshape(
        (ncoefficients, nt), order="F"
    )
    imag = real + np.float32(100.0)
    return np.asfortranarray(real + 1j * imag, dtype=np.complex64)


def test_onedtotwod_expands_triangular_coefficients_with_historical_scale():
    truncation = 3
    nlat = 5
    coefficients = _coefficients(truncation, nt=2)

    real_part, imag_part = _spherepack.onedtotwod(coefficients, nlat)

    assert real_part.dtype == np.float32
    assert imag_part.dtype == np.float32
    assert real_part.shape == (nlat, nlat, 2)
    assert imag_part.shape == (nlat, nlat, 2)

    for zonal_degree in range(truncation + 1):
        for total_degree in range(zonal_degree, truncation + 1):
            index = _compact_index(zonal_degree, total_degree, truncation)
            np.testing.assert_array_equal(
                real_part[zonal_degree, total_degree, :],
                np.float32(2.0) * coefficients[index, :].real,
            )
            np.testing.assert_array_equal(
                imag_part[zonal_degree, total_degree, :],
                np.float32(2.0) * coefficients[index, :].imag,
            )


def test_twodtooned_compacts_triangular_domain_with_historical_scale():
    truncation = 3
    nlat = 5
    nt = 2
    real_part = np.asfortranarray(
        np.arange(nlat * nlat * nt, dtype=np.float32).reshape(
            (nlat, nlat, nt), order="F"
        )
    )
    imag_part = np.asfortranarray(real_part + np.float32(200.0))

    actual = _spherepack.twodtooned(real_part, imag_part, truncation)
    expected = np.empty(
        ((truncation + 1) * (truncation + 2) // 2, nt),
        dtype=np.complex64,
        order="F",
    )

    for zonal_degree in range(truncation + 1):
        for total_degree in range(zonal_degree, truncation + 1):
            index = _compact_index(zonal_degree, total_degree, truncation)
            expected[index, :] = np.float32(0.5) * (
                real_part[zonal_degree, total_degree, :]
                + 1j * imag_part[zonal_degree, total_degree, :]
            )

    assert actual.dtype == np.complex64
    np.testing.assert_array_equal(actual, expected)


def test_scalar_storage_round_trip_preserves_compact_coefficients():
    truncation = 4
    coefficients = _coefficients(truncation, nt=3)

    real_part, imag_part = _spherepack.onedtotwod(coefficients, nlat=6)
    restored = _spherepack.twodtooned(real_part, imag_part, truncation)

    np.testing.assert_array_equal(restored, coefficients)
