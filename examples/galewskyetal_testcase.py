#!/usr/bin/env python3
"""Run a bounded Galewsky et al. shallow-water test-case demonstration.

The historical example integrated six simulated days and required Basemap. This
version uses the maintained :mod:`pyspharm` API, exposes the integration length
as a command-line argument and needs matplotlib only when a figure is requested.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np

import pyspharm


def total_orders(truncation: int) -> np.ndarray:
    """Return the total spherical-harmonic order for triangular storage."""

    return np.asarray(
        [order for degree in range(truncation + 1) for order in range(degree, truncation + 1)],
        dtype=np.float32,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nlon", type=int, default=128, help="regular-grid longitude count")
    parser.add_argument(
        "--ntrunc",
        type=int,
        default=None,
        help="triangular truncation (default: min(42, nlat - 1))",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=24,
        help="number of 150-second time steps (default: 24, one hour)",
    )
    parser.add_argument("--output", type=Path, help="optional PNG/PDF output path")
    parser.add_argument("--show", action="store_true", help="show an interactive plot")
    return parser


def run_case(nlon: int, ntrunc: int, steps: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Integrate the barotropically unstable shallow-water case for ``steps``."""

    if nlon < 8 or nlon % 2:
        raise ValueError("nlon must be an even integer of at least 8")
    nlat = nlon // 2 + 1
    if ntrunc < 1 or ntrunc > nlat - 1:
        raise ValueError(f"ntrunc must be between 1 and {nlat - 1}")
    if steps < 1:
        raise ValueError("steps must be at least 1")

    radius = 6.37122e6
    rotation_rate = 7.292e-5
    gravity = 9.80616
    mean_depth = 1.0e4
    maximum_jet_speed = 80.0
    time_step = np.float32(150.0)
    hyperdiffusion_efold = np.float32(3.0 * 3600.0)
    hyperdiffusion_order = 8

    transform = pyspharm.SphericalHarmonicTransform(
        nlon, nlat, radius=radius, grid="regular"
    )
    longitude_increment = np.float32(2.0 * np.pi / nlon)
    latitude_1d = np.linspace(np.pi / 2.0, -np.pi / 2.0, nlat, dtype=np.float32)
    longitude_1d = -np.pi + longitude_increment * np.arange(nlon, dtype=np.float32)
    longitude, latitude = np.meshgrid(longitude_1d, latitude_1d)
    coriolis = pyspharm.as_real32(2.0 * rotation_rate * np.sin(latitude))

    latitude_lower = np.float32(np.pi / 7.0)
    latitude_upper = np.float32(np.pi / 2.0 - latitude_lower)
    perturbation_latitude = np.float32(np.pi / 4.0)
    exponential_normalizer = np.float32(
        np.exp(-4.0 / (latitude_upper - latitude_lower) ** 2)
    )
    jet_core = (maximum_jet_speed / exponential_normalizer) * np.exp(
        1.0 / ((latitude_1d - latitude_lower) * (latitude_1d - latitude_upper))
    )
    jet_1d = np.where(
        np.logical_and(latitude_1d < latitude_upper, latitude_1d > latitude_lower),
        jet_core,
        0.0,
    ).astype(np.float32)
    zonal_wind = np.asfortranarray(
        np.broadcast_to(jet_1d[:, None], (nlat, nlon)).copy(), dtype=np.float32
    )
    meridional_wind = np.zeros((nlat, nlon), dtype=np.float32, order="F")
    height_bump = pyspharm.as_real32(
        120.0
        * np.cos(latitude)
        * np.exp(-(longitude / np.float32(1.0 / 3.0)) ** 2)
        * np.exp(-(perturbation_latitude - latitude) ** 2 / np.float32(1.0 / 15.0))
    )

    vorticity, divergence = transform.analyze_wind(
        zonal_wind, meridional_wind, truncation=ntrunc
    )
    orders = total_orders(ntrunc)
    laplacian = np.asfortranarray(
        -(orders * (orders + np.float32(1.0)) / np.float32(radius**2)), dtype=np.float32
    )
    inverse_laplacian = np.zeros_like(laplacian)
    inverse_laplacian[1:] = np.float32(1.0) / laplacian[1:]
    hyperdiffusion = np.asfortranarray(
        np.exp(
            (-time_step / hyperdiffusion_efold)
            * (laplacian / laplacian[-1]) ** (hyperdiffusion_order // 2)
        ),
        dtype=np.float32,
    )

    vorticity_grid = transform.synthesize_scalar(vorticity)
    momentum_u = pyspharm.as_real32(zonal_wind * (vorticity_grid + coriolis))
    momentum_v = pyspharm.as_real32(meridional_wind * (vorticity_grid + coriolis))
    balanced_vorticity, _ = transform.analyze_wind(
        momentum_u, momentum_v, truncation=ntrunc
    )
    kinetic_energy = transform.analyze_scalar(
        pyspharm.as_real32(0.5 * (zonal_wind**2 + meridional_wind**2)),
        truncation=ntrunc,
    )
    geopotential_spectrum = np.asfortranarray(
        inverse_laplacian * balanced_vorticity - kinetic_energy, dtype=np.complex64
    )
    geopotential_grid = pyspharm.as_real32(
        gravity * (mean_depth + height_bump)
        + transform.synthesize_scalar(geopotential_spectrum)
    )
    geopotential_spectrum = transform.analyze_scalar(
        geopotential_grid, truncation=ntrunc
    )

    divergence_tendency = np.zeros(vorticity.shape + (3,), dtype=np.complex64, order="F")
    vorticity_tendency = np.zeros(vorticity.shape + (3,), dtype=np.complex64, order="F")
    geopotential_tendency = np.zeros(vorticity.shape + (3,), dtype=np.complex64, order="F")
    newest, current, previous = 0, 1, 2

    started = time.process_time()
    for step in range(steps):
        vorticity_grid = transform.synthesize_scalar(vorticity)
        zonal_wind, meridional_wind = transform.synthesize_wind(vorticity, divergence)
        geopotential_grid = transform.synthesize_scalar(geopotential_spectrum)

        momentum_u = pyspharm.as_real32(zonal_wind * (vorticity_grid + coriolis))
        momentum_v = pyspharm.as_real32(meridional_wind * (vorticity_grid + coriolis))
        divergence_tendency[:, newest], vorticity_tendency[:, newest] = transform.analyze_wind(
            momentum_u, momentum_v, truncation=ntrunc
        )
        vorticity_tendency[:, newest] *= np.complex64(-1.0)

        flux_u = pyspharm.as_real32(zonal_wind * geopotential_grid)
        flux_v = pyspharm.as_real32(meridional_wind * geopotential_grid)
        _, geopotential_tendency[:, newest] = transform.analyze_wind(
            flux_u, flux_v, truncation=ntrunc
        )
        geopotential_tendency[:, newest] *= np.complex64(-1.0)
        bernoulli = transform.analyze_scalar(
            pyspharm.as_real32(
                geopotential_grid + 0.5 * (zonal_wind**2 + meridional_wind**2)
            ),
            truncation=ntrunc,
        )
        divergence_tendency[:, newest] += -laplacian * bernoulli

        if step == 0:
            vorticity_tendency[:, current] = vorticity_tendency[:, newest]
            vorticity_tendency[:, previous] = vorticity_tendency[:, newest]
            divergence_tendency[:, current] = divergence_tendency[:, newest]
            divergence_tendency[:, previous] = divergence_tendency[:, newest]
            geopotential_tendency[:, current] = geopotential_tendency[:, newest]
            geopotential_tendency[:, previous] = geopotential_tendency[:, newest]
        elif step == 1:
            vorticity_tendency[:, previous] = vorticity_tendency[:, newest]
            divergence_tendency[:, previous] = divergence_tendency[:, newest]
            geopotential_tendency[:, previous] = geopotential_tendency[:, newest]

        vorticity += time_step * (
            np.float32(23.0 / 12.0) * vorticity_tendency[:, newest]
            - np.float32(16.0 / 12.0) * vorticity_tendency[:, current]
            + np.float32(5.0 / 12.0) * vorticity_tendency[:, previous]
        )
        divergence += time_step * (
            np.float32(23.0 / 12.0) * divergence_tendency[:, newest]
            - np.float32(16.0 / 12.0) * divergence_tendency[:, current]
            + np.float32(5.0 / 12.0) * divergence_tendency[:, previous]
        )
        geopotential_spectrum += time_step * (
            np.float32(23.0 / 12.0) * geopotential_tendency[:, newest]
            - np.float32(16.0 / 12.0) * geopotential_tendency[:, current]
            + np.float32(5.0 / 12.0) * geopotential_tendency[:, previous]
        )
        vorticity *= hyperdiffusion
        divergence *= hyperdiffusion
        newest, current, previous = previous, newest, current

    elapsed = time.process_time() - started
    vorticity_grid = transform.synthesize_scalar(vorticity)
    geopotential_grid = transform.synthesize_scalar(geopotential_spectrum)
    potential_vorticity = pyspharm.as_real32(
        (0.5 * mean_depth * gravity / rotation_rate)
        * (vorticity_grid + coriolis)
        / geopotential_grid
    )
    return potential_vorticity, longitude_1d, latitude_1d, elapsed


def main() -> None:
    args = build_parser().parse_args()
    nlat = args.nlon // 2 + 1
    ntrunc = args.ntrunc if args.ntrunc is not None else min(42, nlat - 1)
    potential_vorticity, longitude, latitude, elapsed = run_case(
        args.nlon, ntrunc, args.steps
    )
    if not np.all(np.isfinite(potential_vorticity)):
        raise RuntimeError("Galewsky integration produced non-finite potential vorticity")

    simulated_hours = args.steps * 150.0 / 3600.0
    print(f"grid={args.nlon}x{nlat}")
    print(f"truncation={ntrunc}")
    print(f"simulated_hours={simulated_hours:.3f}")
    print(f"cpu_seconds={elapsed:.3f}")
    print(f"potential_vorticity_minimum={np.min(potential_vorticity):.6e}")
    print(f"potential_vorticity_maximum={np.max(potential_vorticity):.6e}")

    if args.output is None and not args.show:
        return

    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    image = axis.contourf(
        np.rad2deg(longitude), np.rad2deg(latitude), potential_vorticity, levels=21
    )
    figure.colorbar(image, ax=axis, label="dimensionless potential vorticity")
    axis.set_xlabel("longitude (degrees)")
    axis.set_ylabel("latitude (degrees)")
    axis.set_title(
        f"Galewsky shallow-water case: T{ntrunc}, {simulated_hours:.2f} h"
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(args.output, dpi=150)
        print(f"figure={args.output}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
