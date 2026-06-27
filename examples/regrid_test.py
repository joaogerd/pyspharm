#!/usr/bin/env python3
"""Regrid a Rossby--Haurwitz wave and check spectral interpolation.

Run the representative case with::

    python examples/regrid_test.py

Use ``--small`` for a fast smoke case suitable for development and CI.
"""

from __future__ import annotations

import argparse
import math

import numpy as np

import pyspharm
from spharm import gaussian_lats_wts, getgeodesicpts, legendre, specintrp


def rossby_haurwitz_wave(
    wavenumber: float,
    angular_velocity: float,
    radius: float,
    latitude: np.ndarray,
    longitude: np.ndarray,
) -> np.ndarray:
    """Return a deterministic Rossby--Haurwitz streamfunction field."""

    return (
        -radius**2 * angular_velocity * np.sin(latitude)
        + radius**2
        * angular_velocity
        * np.cos(latitude) ** wavenumber
        * np.sin(latitude)
        * np.cos(wavenumber * longitude)
    )


def normalized_error(actual: np.ndarray, expected: np.ndarray) -> float:
    """Return an L-infinity error normalized by the exact-field amplitude."""

    return float(np.max(np.abs(actual - expected)) / np.max(np.abs(expected)))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--small",
        action="store_true",
        help="run a reduced-resolution smoke case",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.small:
        regular_nlon, regular_nlat = 64, 33
        gaussian_nlon, gaussian_nlat = 72, 36
        geodesic_edges = 3
    else:
        regular_nlon, regular_nlat = 144, 73
        gaussian_nlon, gaussian_nlat = 192, 94
        geodesic_edges = 7

    wavenumber = 4.0
    angular_velocity = 7.848e-6
    radius = 6.371e6

    regular_latitude = np.linspace(
        np.pi / 2.0, -np.pi / 2.0, regular_nlat, dtype=np.float32
    )
    regular_longitude = np.linspace(
        0.0, 2.0 * np.pi, regular_nlon, endpoint=False, dtype=np.float32
    )
    regular_lon, regular_lat = np.meshgrid(regular_longitude, regular_latitude)
    regular_exact = pyspharm.as_real32(
        rossby_haurwitz_wave(
            wavenumber, angular_velocity, radius, regular_lat, regular_lon
        )
    )

    gaussian_latitude_degrees, _ = gaussian_lats_wts(gaussian_nlat)
    gaussian_latitude = np.deg2rad(gaussian_latitude_degrees).astype(np.float32)
    gaussian_longitude = np.linspace(
        0.0, 2.0 * np.pi, gaussian_nlon, endpoint=False, dtype=np.float32
    )
    gaussian_lon, gaussian_lat = np.meshgrid(gaussian_longitude, gaussian_latitude)
    gaussian_field = pyspharm.as_real32(
        rossby_haurwitz_wave(
            wavenumber, angular_velocity, radius, gaussian_lat, gaussian_lon
        )
    )

    regular_transform = pyspharm.SphericalHarmonicTransform(
        regular_nlon, regular_nlat, radius=radius, grid="regular"
    )
    gaussian_transform = pyspharm.SphericalHarmonicTransform(
        gaussian_nlon, gaussian_nlat, radius=radius, grid="gaussian"
    )
    regular_field = pyspharm.regrid_scalar(
        gaussian_transform, regular_transform, gaussian_field
    )

    regridding_error = normalized_error(regular_field, regular_exact)
    print(f"regridding_normalized_error={regridding_error:.6e}")

    truncation = regular_nlat - 1
    coefficients = regular_transform.analyze_scalar(regular_exact, truncation=truncation)
    latitude_points, longitude_points = getgeodesicpts(geodesic_edges)
    interpolation_errors = []
    for latitude_degrees, longitude_degrees in zip(latitude_points, longitude_points):
        associated_legendre = legendre(latitude_degrees, truncation)
        interpolated = specintrp(longitude_degrees, coefficients, associated_legendre)
        exact = rossby_haurwitz_wave(
            wavenumber,
            angular_velocity,
            radius,
            np.deg2rad(latitude_degrees),
            np.deg2rad(longitude_degrees),
        )
        interpolation_errors.append(abs(exact - interpolated))

    interpolation_error = float(max(interpolation_errors) / np.max(np.abs(regular_exact)))
    print(f"interpolation_normalized_error={interpolation_error:.6e}")

    if not math.isfinite(regridding_error) or not math.isfinite(interpolation_error):
        raise RuntimeError("spectral example produced a non-finite error")


if __name__ == "__main__":
    main()
