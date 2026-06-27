"""Regression test for a reviewed legacy numerical reference snapshot."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.reference.baseline import CONTRACT_VERSION, validate_snapshot


DEFAULT_REFERENCE = Path("tests/reference/data") / f"{CONTRACT_VERSION}.npz"


def test_legacy_numerical_contract() -> None:
    """The modernized backend must reproduce the reviewed legacy snapshot."""

    reference = Path(os.environ.get("PYSPHARM_LEGACY_REFERENCE", DEFAULT_REFERENCE))
    if not reference.is_file():
        pytest.skip(
            "No reviewed legacy reference snapshot is available yet. "
            "Run tests/reference/generate_legacy_baseline.py in the designated "
            "legacy build environment and commit the resulting .npz file."
        )
    validate_snapshot(reference)
