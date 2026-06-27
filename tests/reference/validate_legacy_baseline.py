#!/usr/bin/env python3
"""Validate the current implementation against a legacy reference snapshot."""

from __future__ import annotations

import argparse
from pathlib import Path

from tests.reference.baseline import (
    CONTRACT_VERSION,
    DEFAULT_ATOL,
    DEFAULT_RTOL,
    validate_snapshot,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path("tests/reference/data") / f"{CONTRACT_VERSION}.npz",
        help="reference .npz file (default: %(default)s)",
    )
    parser.add_argument("--rtol", type=float, default=DEFAULT_RTOL)
    parser.add_argument("--atol", type=float, default=DEFAULT_ATOL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_snapshot(args.reference, rtol=args.rtol, atol=args.atol)
    print(f"Validated {CONTRACT_VERSION}: {args.reference}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
