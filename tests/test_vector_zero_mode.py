"""Tests for the non-representable global vector spectral mode."""

from __future__ import annotations

import numpy as np

import spharm


def test_getuv_discards_global_vorticity_and_divergence_modes():
    transform = spharm.Spharmt(16, 8, gridtype="gaussian", legfunc="computed")
    truncation = 3
    ncoefficients = (truncation + 1) * (truncation + 2) // 2
    zeros = np.zeros(ncoefficients, dtype=np.complex64)
    global_modes = zeros.copy()
    global_modes[0] = np.complex64(3.0 - 2.0j)

    expected_u, expected_v = transform.getuv(zeros, zeros)
    actual_u, actual_v = transform.getuv(global_modes, -global_modes)

    np.testing.assert_allclose(actual_u, expected_u, rtol=0.0, atol=2.0e-6)
    np.testing.assert_allclose(actual_v, expected_v, rtol=0.0, atol=2.0e-6)
    assert np.all(np.isfinite(actual_u))
    assert np.all(np.isfinite(actual_v))
