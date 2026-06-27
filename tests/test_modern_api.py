"""Contract tests for the maintained :mod:`pyspharm` API."""

import numpy as np
import pytest

import pyspharm


@pytest.fixture
def transform() -> pyspharm.SphericalHarmonicTransform:
    return pyspharm.SphericalHarmonicTransform(64, 32, grid="gaussian")


def test_scalar_roundtrip_uses_explicit_native_precision(transform):
    field = np.ones((32, 64), dtype=np.float32, order="F")

    coefficients = transform.analyze_scalar(field, truncation=21)
    restored = transform.synthesize_scalar(coefficients)

    assert coefficients.dtype == np.complex64
    assert coefficients.shape == ((21 + 1) * (21 + 2) // 2,)
    assert restored.dtype == np.float32
    assert restored.shape == field.shape
    assert np.allclose(restored, field, rtol=2.0e-5, atol=2.0e-5)


def test_wind_api_delegates_to_legacy_vector_transforms(transform):
    zonal = np.zeros((32, 64), dtype=np.float32, order="F")
    meridional = np.zeros((32, 64), dtype=np.float32, order="F")

    vorticity, divergence = transform.analyze_wind(
        zonal, meridional, truncation=21
    )
    restored_zonal, restored_meridional = transform.synthesize_wind(
        vorticity, divergence
    )

    assert vorticity.dtype == divergence.dtype == np.complex64
    assert restored_zonal.dtype == restored_meridional.dtype == np.float32
    assert restored_zonal.shape == restored_meridional.shape == (32, 64)
    assert np.all(np.isfinite(restored_zonal))
    assert np.all(np.isfinite(restored_meridional))


def test_precision_boundary_is_explicit(transform):
    field64 = np.ones((32, 64), dtype=np.float64)

    with pytest.raises(pyspharm.PrecisionError, match="as_real32"):
        transform.analyze_scalar(field64)

    native_field = pyspharm.as_real32(field64)
    coefficients = transform.analyze_scalar(native_field, truncation=21)
    native_coefficients = pyspharm.as_complex64(coefficients)

    assert native_field.dtype == np.float32
    assert native_field.flags.f_contiguous
    assert native_coefficients.dtype == np.complex64
    assert native_coefficients.flags.f_contiguous


def test_spectral_shape_is_checked(transform):
    invalid = np.ones(10, dtype=np.complex64)

    with pytest.raises(ValueError, match="coefficient count"):
        transform.synthesize_scalar(invalid)


def test_configuration_is_immutable_and_validated():
    configuration = pyspharm.GridConfiguration(64, 32, grid="regular")

    assert configuration.nlon == 64
    assert configuration.nlat == 32
    with pytest.raises(ValueError, match="at least 4"):
        pyspharm.GridConfiguration(3, 32)
    with pytest.raises(ValueError, match="either 'regular' or 'gaussian'"):
        pyspharm.GridConfiguration(64, 32, grid="unsupported")
