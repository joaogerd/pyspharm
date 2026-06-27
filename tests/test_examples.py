"""Smoke tests for documented examples without optional plotting dependencies."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("arguments", "expected_output"),
    [
        (("examples/regrid_test.py", "--small"), "regridding_normalized_error="),
        (("examples/geodesic.py", "--edge-points", "3"), "points="),
        (
            (
                "examples/spharmonic.py",
                "--nlon",
                "64",
                "--nlat",
                "33",
                "--degree",
                "3",
                "--order",
                "6",
            ),
            "coefficient_index=",
        ),
        (
            (
                "examples/galewskyetal_testcase.py",
                "--nlon",
                "32",
                "--ntrunc",
                "10",
                "--steps",
                "2",
            ),
            "potential_vorticity_maximum=",
        ),
    ],
)
def test_example_runs_without_plot(arguments: tuple[str, ...], expected_output: str):
    environment = os.environ.copy()
    environment.setdefault("MPLBACKEND", "Agg")
    completed = subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
        check=True,
        timeout=120,
    )

    assert expected_output in completed.stdout
