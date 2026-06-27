"""Contract tests for the maintained :mod:`pyspharm` API."""

import numpy as np
import pytest

import pyspharm
import spharm


@pytest.fixture
def transform() -> pyspharm.SphericalHarmonicTransform:
    return pyspharm.SphericalHarmonicTransform(64, 32, grid="gaussian")


def _wind_fields() -> tuple[np.ndarray, np.ndarray]:
    """Return deterministic non-zero wind fields in the legacy ABI precision."""

    longitude = np.arange(64, dtype=np.float32) * (2.0 * np.pi / 64.0)
    latitude = np.linspace(np.pi / 2.0, -np.pi / 2.0, 32, dtype=np.float32)
    lon, lat = np.meshgrid(longitude, latitude)
    zonal = np.asfortranarray(np.cos(lat) * np.sin(lon), dtype=np.float32)
    meridional = np.asfortranarray(np.sin(2.0 * lat) * np.cos(lon), dtype=np.float32)
    return zonal, meridional


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


@pytest.mark.parametrize("grid", ["regular", "gaussian"])
def test_diagnostic_methods_match_legacy_engine(grid):
    transform = pyspharm.SphericalHarmonicTransform(64, 32, grid=grid)
    legacy = spharm.Spharmt(64, 32, gridtype=grid)
    zonal, meridional = _wind_fields()

    expected_streamfunction, expected_velocity_potential = legacy.getpsichi(
        zonal, meridional, ntrunc=21
    )
    streamfunction, velocity_potential = transform.streamfunction_velocity_potential(
        zonal, meridional, truncation=21
    )

    assert streamfunction.dtype == velocity_potential.dtype == np.float32
    assert streamfunction.flags.f_contiguous
    assert velocity_potential.flags.f_contiguous
    np.testing.assert_allclose(streamfunction, expected_streamfunction, rtol=2.0e-5, atol=2.0e-5)
    np.testing.assert_allclose(
        velocity_potential, expected_velocity_potential, rtol=2.0e-5, atol=2.0e-5
    )

    coefficients = transform.analyze_scalar(zonal, truncation=21)
    expected_zonal_gradient, expected_meridional_gradient = legacy.getgrad(coefficients)
    zonal_gradient, meridional_gradient = transform.gradient(coefficients)

    assert zonal_gradient.dtype == meridional_gradient.dtype == np.float32
    assert zonal_gradient.flags.f_contiguous
    assert meridional_gradient.flags.f_contiguous
    np.testing.assert_allclose(zonal_gradient, expected_zonal_gradient, rtol=2.0e-5, atol=2.0e-5)
    np.testing.assert_allclose(
        meridional_gradient, expected_meridional_gradient, rtol=2.0e-5, atol=2.0e-5
    )


def test_wind_diagnostic_input_validation(transform):
    zonal, meridional = _wind_fields()

    with pytest.raises(ValueError, match="same shape"):
        transform.streamfunction_velocity_potential(
            zonal, np.expand_dims(meridional, axis=-1)
        )

    with pytest.raises(pyspharm.PrecisionError, match="as_complex64"):
        transform.gradient(np.ones(253, dtype=np.complex128))


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
    invalid = np.ones(11, dtype=np.complex64)

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
