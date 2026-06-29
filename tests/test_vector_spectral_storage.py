"""Regression tests for compact and expanded vector spectral storage."""

from __future__ import annotations

import numpy as np

from spharm import _spherepack


def _index(m: int, n: int, truncation: int) -> int:
    return sum(truncation - order + 1 for order in range(m)) + n - m


def _coefficients(truncation: int, nt: int, offset: float) -> np.ndarray:
    count = (truncation + 1) * (truncation + 2) // 2
    real = np.arange(1, count * nt + 1, dtype=np.float32).reshape(
        (count, nt), order="F"
    ) + np.float32(offset)
    return np.asfortranarray(real + 1j * (real + np.float32(100.0)), dtype=np.complex64)


def test_vector_expansion_preserves_degree_factors_signs_and_zero_mode():
    truncation, nlat = 3, 5
    radius = np.float32(10.0)
    vortex = _coefficients(truncation, 2, 0.0)
    divergence = _coefficients(truncation, 2, 50.0)

    br, bi, cr, ci = _spherepack.onedtotwod_vrtdiv(vortex, divergence, nlat, radius)

    for array in (br, bi, cr, ci):
        np.testing.assert_array_equal(array[0, 0, :], np.float32(0.0))

    for m in range(truncation + 1):
        for n in range(max(m, 1), truncation + 1):
            factor = np.float32(2.0) * radius / np.sqrt(np.float32(n * (n + 1)))
            index = _index(m, n, truncation)
            np.testing.assert_allclose(br[m, n, :], -factor * divergence[index, :].real, rtol=2e-6, atol=2e-6)
            np.testing.assert_allclose(bi[m, n, :], -factor * divergence[index, :].imag, rtol=2e-6, atol=2e-6)
            np.testing.assert_allclose(cr[m, n, :], factor * vortex[index, :].real, rtol=2e-6, atol=2e-6)
            np.testing.assert_allclose(ci[m, n, :], factor * vortex[index, :].imag, rtol=2e-6, atol=2e-6)


def test_vector_compaction_preserves_degree_factors_signs_and_zero_mode():
    truncation, nlat, nt = 3, 5, 2
    radius = np.float32(10.0)
    br = np.asfortranarray(np.arange(nlat * nlat * nt, dtype=np.float32).reshape((nlat, nlat, nt), order="F"))
    bi = np.asfortranarray(br + np.float32(100.0))
    cr = np.asfortranarray(br + np.float32(200.0))
    ci = np.asfortranarray(br + np.float32(300.0))

    vortex, divergence = _spherepack.twodtooned_vrtdiv(br, bi, cr, ci, truncation, radius)
    expected_vortex = np.zeros_like(vortex)
    expected_divergence = np.zeros_like(divergence)

    for m in range(truncation + 1):
        for n in range(max(m, 1), truncation + 1):
            factor = np.float32(0.5) * np.sqrt(np.float32(n * (n + 1))) / radius
            index = _index(m, n, truncation)
            expected_divergence[index, :] = -factor * (br[m, n, :] + 1j * bi[m, n, :])
            expected_vortex[index, :] = factor * (cr[m, n, :] + 1j * ci[m, n, :])

    np.testing.assert_allclose(vortex, expected_vortex, rtol=2e-6, atol=2e-6)
    np.testing.assert_allclose(divergence, expected_divergence, rtol=2e-6, atol=2e-6)


def test_vector_storage_round_trip_preserves_nonzero_degrees():
    truncation = 4
    radius = np.float32(6.3712e6)
    vortex = _coefficients(truncation, 3, 0.0)
    divergence = _coefficients(truncation, 3, 50.0)

    br, bi, cr, ci = _spherepack.onedtotwod_vrtdiv(vortex, divergence, 6, radius)
    actual_vortex, actual_divergence = _spherepack.twodtooned_vrtdiv(br, bi, cr, ci, truncation, radius)
    vortex[0, :] = np.complex64(0.0)
    divergence[0, :] = np.complex64(0.0)

    np.testing.assert_allclose(actual_vortex, vortex, rtol=3e-6, atol=3e-6)
    np.testing.assert_allclose(actual_divergence, divergence, rtol=3e-6, atol=3e-6)
