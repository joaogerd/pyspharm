#!/usr/bin/env python3
"""Smoke-test the maintained API after installing a release artifact.

This script is executed from outside the source checkout by package and release
workflows. It intentionally imports only the installed distribution.
"""

from __future__ import annotations

import numpy as np

import pyspharm


def main() -> None:
    source = pyspharm.SphericalHarmonicTransform(64, 32, grid="regular")
    destination = pyspharm.SphericalHarmonicTransform(48, 25, grid="gaussian")
    field = pyspharm.as_real32(np.ones((source.nlat, source.nlon)))

    coefficients = source.analyze_scalar(field, truncation=21)
    zonal_gradient, meridional_gradient = source.gradient(coefficients)
    assert zonal_gradient.shape == field.shape
    assert meridional_gradient.shape == field.shape

    zero_wind = np.zeros_like(field, dtype=np.float32, order="F")
    streamfunction, velocity_potential = source.streamfunction_velocity_potential(
        zero_wind, zero_wind, truncation=21
    )
    assert streamfunction.shape == field.shape
    assert velocity_potential.shape == field.shape

    regridded = pyspharm.regrid_scalar(source, destination, field, truncation=21)
    assert regridded.shape == (destination.nlat, destination.nlon)
    assert regridded.dtype == np.float32

    latitude, weights = pyspharm.gaussian_latitudes_weights(destination.nlat)
    assert latitude.shape == (destination.nlat,)
    assert weights.shape == (destination.nlat,)
    zonal_wavenumber, total_wavenumber = pyspharm.spectral_indices(21)
    assert zonal_wavenumber.shape == coefficients.shape
    assert total_wavenumber.shape == coefficients.shape
    geodesic_latitude, geodesic_longitude = pyspharm.geodesic_points(3)
    assert geodesic_latitude.shape == geodesic_longitude.shape

    value = pyspharm.interpolate_scalar(
        coefficients, latitude=0.0, longitude=0.0
    )
    assert np.isfinite(value)


if __name__ == "__main__":
    main()
