#!/usr/bin/env python3
"""Generate points on an icosahedral spherical geodesic.

The numerical calculation runs without optional plotting dependencies. Use
``--output`` or ``--show`` to generate a longitude-latitude plot.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import pyspharm


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--edge-points",
        type=int,
        default=7,
        help="number of points along an icosahedron edge (default: 7)",
    )
    parser.add_argument("--output", type=Path, help="optional PNG/PDF output path")
    parser.add_argument("--show", action="store_true", help="show an interactive plot")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    latitude, longitude = pyspharm.geodesic_points(args.edge_points)
    print(f"points={latitude.size}")
    print(f"latitude_range=[{np.min(latitude):.3f}, {np.max(latitude):.3f}]")
    print(f"longitude_range=[{np.min(longitude):.3f}, {np.max(longitude):.3f}]")

    if args.output is None and not args.show:
        return

    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(9, 4.5), constrained_layout=True)
    axis.scatter(longitude, latitude, s=16)
    axis.set_xlabel("longitude (degrees)")
    axis.set_ylabel("latitude (degrees)")
    axis.set_title(f"Icosahedral geodesic, {args.edge_points} edge points")
    axis.set_xlim(-180, 180)
    axis.set_ylim(-90, 90)
    axis.grid(True)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(args.output, dpi=150)
        print(f"figure={args.output}")
    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
