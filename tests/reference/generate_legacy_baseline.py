#!/usr/bin/env python3
"""Capture the deterministic legacy numerical contract as an NPZ snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from tests.reference.baseline import CONTRACT_VERSION, write_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("tests/reference/data") / f"{CONTRACT_VERSION}.npz",
        help="destination .npz file (default: %(default)s)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow replacement of an existing snapshot after review",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    destination = write_snapshot(args.output, overwrite=args.force)
    print(f"Wrote {CONTRACT_VERSION} reference snapshot: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
