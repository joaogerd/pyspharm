# pyspharm-ng

`pyspharm-ng` is the maintained successor to the historical `pyspharm`
Python interface for NCAR/UCAR SPHEREPACK spherical-harmonic transforms.

The distribution name is **`pyspharm-ng`**. This compatibility phase provides
both a maintained public interface and the historical compatibility interface:

```python
import pyspharm

transform = pyspharm.SphericalHarmonicTransform(
    nlon=144,
    nlat=72,
    grid="gaussian",
)
field = pyspharm.as_real32(field_from_application)
coefficients = transform.analyze_scalar(field, truncation=42)
restored = transform.synthesize_scalar(coefficients)
```

The maintained API uses explicit native precision: transform inputs are
`float32` fields or `complex64` coefficients. Use `as_real32` and
`as_complex64` to make a conversion explicit.

Existing code continues to use the historical import path:

```python
import spharm

transform = spharm.Spharmt(144, 72, gridtype="gaussian")
```

See [the Stage 4 API guide](docs/modernization/04-python-api.md) for the
method mapping and migration boundary.

## Installation

Published wheels will be available in a later release. Until then, install
from a source checkout with a supported Python and a Fortran compiler:

```bash
python -m pip install --upgrade pip
python -m pip install .
```

The build uses the PEP 517 Meson backend. A source installation requires a
working C compiler and `gfortran` (or a compatible Fortran compiler).

For development and tests:

```bash
python -m pip install -e ".[tests]"
python -m pytest
```

To build distributable artifacts:

```bash
python -m pip install build
python -m build
```

The project CI installs both the generated wheel and the source distribution
into clean virtual environments and runs an import-and-transform smoke test.

## Compatibility contract

The current numerical implementation is preserved as a documented legacy
contract. Before modifying the Fortran algorithms or the scientific API, run:

```bash
python tests/reference/validate_legacy_baseline.py
```

The checked-in reference covers regular and Gaussian grids with both stored and
computed Legendre workspaces. Details are in
[the scientific baseline document](docs/modernization/01-scientific-baseline.md).

## License and provenance

This repository is a mixed-license distribution. It contains SPHEREPACK-
derived code under the UCAR/NCAR license and historical Python-binding code
under its original permission notice. New maintained-project files use the
BSD 3-Clause license unless stated otherwise. Read [LICENSE](LICENSE) and
[NOTICE](NOTICE) before redistributing the package.

## Modernization status

The modernization plan is tracked in [docs/modernization/README.md](docs/modernization/README.md).
Stages 2 and 3 establish modern packaging, compatibility and a free-form
Fortran build path. Stage 4 adds the maintained `pyspharm` API while preserving
`spharm` for existing applications.
