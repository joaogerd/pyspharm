"""Regression tests for ABI-preserving modern Fortran spectral operators."""

from __future__ import annotations

import numpy as np

from spharm import _spherepack


def _coefficient_degrees(truncation: int) -> np.ndarray:
    """Return total degree for the historical compact triangular ordering."""

    return np.asarray(
        [
            total_degree
            for zonal_degree in range(truncation + 1)
            for total_degree in range(zonal_degree, truncation + 1)
        ],
        dtype=np.float32,
    )


def _coefficients(truncation: int, nt: int) -> np.ndarray:
    ncoefficients = (truncation + 1) * (truncation + 2) // 2
    real = np.arange(1, ncoefficients * nt + 1, dtype=np.float32).reshape(
        (ncoefficients, nt), order="F"
    )
    imaginary = real + np.float32(100.0)
    return np.asfortranarray(real + np.complex64(1j) * imaginary, dtype=np.complex64)


def test_laplacian_matches_analytical_spectral_factor():
    truncation = 3
    radius = np.float32(2.5)
    coefficients = _coefficients(truncation, nt=2)
    degrees = _coefficient_degrees(truncation)
    factor = -(degrees * (degrees + np.float32(1.0)) / radius**2)

    actual = _spherepack.lap(coefficients, radius)
    expected = np.asfortranarray(factor[:, None] * coefficients, dtype=np.complex64)

    assert actual.dtype == np.complex64
    assert actual.flags.f_contiguous
    np.testing.assert_allclose(actual, expected, rtol=2.0e-6, atol=2.0e-6)


def test_inverse_laplacian_matches_analytical_spectral_factor():
    truncation = 3
    radius = np.float32(2.5)
    coefficients = _coefficients(truncation, nt=2)
    degrees = _coefficient_degrees(truncation)
    factor = np.zeros_like(degrees)
    nonzero = degrees > np.float32(0.0)
    factor[nonzero] = -(radius**2 / (degrees[nonzero] * (degrees[nonzero] + 1.0)))

    actual = _spherepack.invlap(coefficients, radius)
    expected = np.asfortranarray(factor[:, None] * coefficients, dtype=np.complex64)

    assert actual.dtype == np.complex64
    assert actual.flags.f_contiguous
    np.testing.assert_allclose(actual, expected, rtol=2.0e-6, atol=2.0e-6)


def test_inverse_laplacian_undoes_laplacian_except_global_mean():
    coefficients = _coefficients(truncation=4, nt=3)
    radius = np.float32(6.3712e6)

    restored = _spherepack.invlap(_spherepack.lap(coefficients, radius), radius)
    expected = coefficients.copy(order="F")
    expected[0, :] = np.complex64(0.0)

    np.testing.assert_allclose(restored, expected, rtol=3.0e-6, atol=3.0e-6)


def test_spectral_smoothing_matches_total_degree_factors():
    truncation = 4
    coefficients = _coefficients(truncation, nt=3)
    degrees = _coefficient_degrees(truncation).astype(np.intp)
    smoothing = np.asarray([1.0, 0.9, 0.7, 0.4, 0.1], dtype=np.float32)

    actual = _spherepack.multsmoothfact(coefficients, smoothing)
    expected = np.asfortranarray(
        smoothing[degrees, None] * coefficients,
        dtype=np.complex64,
    )

    assert actual.dtype == np.complex64
    assert actual.flags.f_contiguous
    np.testing.assert_allclose(actual, expected, rtol=0.0, atol=0.0)


def test_spectral_smoothing_preserves_coefficients_for_unit_factors():
    coefficients = _coefficients(truncation=5, nt=2)
    smoothing = np.ones(6, dtype=np.float32)

    actual = _spherepack.multsmoothfact(coefficients, smoothing)

    np.testing.assert_array_equal(actual, coefficients)
