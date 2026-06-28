#!/usr/bin/env python3
"""Synthesize and optionally plot one real spherical harmonic basis field.

The example uses the maintained :mod:`pyspharm` API and creates no plot unless
``--output`` or ``--show`` is requested.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import pyspharm


def coefficient_index(degree: int, order: int, truncation: int) -> int:
    """Return the compact-storage index for zonal degree ``m`` and order ``n``."""

    zonal_wavenumber, total_wavenumber = pyspharm.spectral_indices(truncation)
    matches = np.flatnonzero(
        np.logical_and(zonal_wavenumber == degree, total_wavenumber == order)
    )
    if matches.size != 1:
        raise ValueError(
            "degree and order must satisfy 0 <= degree <= order <= truncation"
        )
    return int(matches[0])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--degree", type=int, default=3, help="zonal degree m")
    parser.add_argument("--order", type=int, default=6, help="total order n")
    parser.add_argument("--nlon", type=int, default=360, help="longitude count")
    parser.add_argument("--nlat", type=int, default=181, help="latitude count")
    parser.add_argument("--output", type=Path, help="optional PNG/PDF output path")
    parser.add_argument("--show", action="store_true", help="show an interactive plot")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    transform = pyspharm.SphericalHarmonicTransform(
        args.nlon, args.nlat, grid="regular", legendre="computed"
    )
    truncation = transform.nlat - 1
    index = coefficient_index(args.degree, args.order, truncation)
    coefficients = np.zeros(
        (truncation + 1) * (truncation + 2) // 2, dtype=np.complex64, order="F"
    )
    coefficients[index] = np.complex64(1.0)
    field = transform.synthesize_scalar(coefficients)

    print(f"truncation={truncation}")
    print(f"coefficient_index={index}")
    print(f"minimum={np.min(field):.6e}")
    print(f"maximum={np.max(field):.6e}")

    if args.output is None and not args.show:
        return

    import matplotlib.pyplot as plt

    longitude = np.linspace(0.0, 360.0, args.nlon, endpoint=False)
    latitude = np.linspace(90.0, -90.0, args.nlat)
    figure, axis = plt.subplots(figsize=(10, 4.5), constrained_layout=True)
    image = axis.contourf(longitude, latitude, field, levels=21)
    figure.colorbar(image, ax=axis, label="amplitude")
    axis.set_xlabel("longitude (degrees east)")
    axis.set_ylabel("latitude (degrees)")
    axis.set_title(
        f"Spherical harmonic: degree m={args.degree}, order n={args.order}"
    )
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(args.output, dpi=150)
        print(f"figure={args.output}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
