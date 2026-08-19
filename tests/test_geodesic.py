"""Geometry tests for the geodesic point generator."""

from __future__ import annotations

import numpy as np

import pyspharm
from spharm import _spherepack


def test_ihgeod_returns_unit_sphere_coordinates():
    x, y, z = _spherepack.ihgeod(5)

    assert x.dtype == np.float32
    assert y.dtype == np.float32
    assert z.dtype == np.float32
    assert x.shape == (9, 5, 5)
    assert y.shape == x.shape
    assert z.shape == x.shape
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(y))
    assert np.all(np.isfinite(z))

    radius = np.sqrt(x * x + y * y + z * z)
    np.testing.assert_allclose(radius, np.float32(1.0), rtol=2.0e-6, atol=2.0e-6)


def test_ihgeod_has_fivefold_longitudinal_symmetry_at_first_edge_point():
    x, y, z = _spherepack.ihgeod(4)
    longitude = np.degrees(np.arctan2(y[0, 0, :], x[0, 0, :]))
    longitude = np.mod(longitude, 360.0)
    deltas = np.mod(np.diff(np.r_[longitude, longitude[0] + 360.0]), 360.0)

    np.testing.assert_allclose(deltas, np.full(5, 72.0, dtype=np.float32), atol=2.0e-5)
    np.testing.assert_allclose(z[0, 0, :], z[0, 0, 0], rtol=0.0, atol=2.0e-6)


def test_geodesic_points_edge_two_are_icosahedron_vertices():
    latitude, longitude = pyspharm.geodesic_points(2)

    assert latitude.dtype == np.float32
    assert longitude.dtype == np.float32
    assert latitude.shape == (12,)
    assert longitude.shape == (12,)
    assert np.all(np.isfinite(latitude))
    assert np.all(np.isfinite(longitude))

    np.testing.assert_array_equal(latitude[:2], np.asarray([90.0, -90.0], dtype=np.float32))
    np.testing.assert_array_equal(longitude[:2], np.asarray([0.0, 0.0], dtype=np.float32))

    expected_ring_latitude = np.degrees(np.arctan(np.float32(0.5)))
    rounded = np.round(latitude[2:], decimals=4)
    north_ring = np.count_nonzero(np.isclose(rounded, expected_ring_latitude, atol=1.0e-4))
    south_ring = np.count_nonzero(np.isclose(rounded, -expected_ring_latitude, atol=1.0e-4))
    assert north_ring == 5
    assert south_ring == 5


def test_geodesic_points_edge_one_returns_only_poles():
    latitude, longitude = pyspharm.geodesic_points(1)

    np.testing.assert_array_equal(latitude, np.asarray([90.0, -90.0], dtype=np.float32))
    np.testing.assert_array_equal(longitude, np.asarray([0.0, 0.0], dtype=np.float32))
