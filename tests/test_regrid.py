"""Tests for the maintained scalar regridding interface."""

import numpy as np
import pytest

import pyspharm
import spharm


def _source_field(nlat: int, nlon: int) -> np.ndarray:
    latitude = np.linspace(np.pi / 2.0, -np.pi / 2.0, nlat, dtype=np.float32)
    longitude = np.linspace(0.0, 2.0 * np.pi, nlon, endpoint=False, dtype=np.float32)
    lon, lat = np.meshgrid(longitude, latitude)
    return np.asfortranarray(np.cos(lat) * np.sin(3.0 * lon), dtype=np.float32)


def test_regrid_scalar_matches_legacy_engine():
    source = pyspharm.SphericalHarmonicTransform(64, 32, grid="gaussian")
    destination = pyspharm.SphericalHarmonicTransform(48, 25, grid="regular")
    legacy_source = spharm.Spharmt(64, 32, gridtype="gaussian")
    legacy_destination = spharm.Spharmt(48, 25, gridtype="regular")
    field = _source_field(source.nlat, source.nlon)

    expected = spharm.regrid(legacy_source, legacy_destination, field, ntrunc=20)
    actual = pyspharm.regrid_scalar(source, destination, field, truncation=20)

    assert actual.dtype == np.float32
    assert actual.flags.f_contiguous
    assert actual.shape == (destination.nlat, destination.nlon)
    np.testing.assert_allclose(actual, expected, rtol=2.0e-5, atol=2.0e-5)


def test_regrid_scalar_validates_smoothing_and_radius():
    source = pyspharm.SphericalHarmonicTransform(64, 32, grid="gaussian")
    destination = pyspharm.SphericalHarmonicTransform(48, 25, grid="regular")
    field = _source_field(source.nlat, source.nlon)

    with pytest.raises(pyspharm.PrecisionError, match="smoothing"):
        pyspharm.regrid_scalar(
            source, destination, field, smoothing=np.ones(destination.nlat)
        )

    other_radius = pyspharm.SphericalHarmonicTransform(
        48, 25, grid="regular", radius=6.4e6
    )
    with pytest.raises(ValueError, match="same sphere radius"):
        pyspharm.regrid_scalar(source, other_radius, field)
