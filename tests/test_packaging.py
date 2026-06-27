"""Tests for the maintained distribution boundary and Python 3 repairs."""

from __future__ import annotations

import importlib
from importlib.metadata import version

import numpy as np
import spharm


def test_distribution_version_is_exposed_by_compatibility_package() -> None:
    assert spharm.__version__ == version("pyspharm-ng")


def test_compiled_extension_is_package_local() -> None:
    extension = importlib.import_module("spharm._spherepack")
    assert extension.__name__ == "spharm._spherepack"


def test_workspace_sizes_are_integers_on_python3() -> None:
    """Constructing a transform must not pass float workspace lengths to F2PY."""

    transform = spharm.Spharmt(64, 32, gridtype="gaussian", legfunc="stored")
    field = np.ones((32, 64), dtype=np.float32, order="F")
    coefficients = transform.grdtospec(field, ntrunc=21)

    assert coefficients.shape == (253,)
    assert np.all(np.isfinite(coefficients))
