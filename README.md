# pyspharm-ng

`pyspharm-ng` is the maintained successor to the historical `pyspharm`
Python interface for NCAR/UCAR SPHEREPACK spherical-harmonic transforms.

The distribution name is **`pyspharm-ng`**.  This compatibility phase keeps the
historical Python import path and public interface:

```python
import spharm

transform = spharm.Spharmt(144, 72, gridtype="gaussian")
```

A new `pyspharm` API will be introduced separately after the legacy contract
and packaging are stable.  Existing code should therefore continue to import
`spharm` for now.

## Installation

Published wheels will be available in a later release.  Until then, install
from a source checkout with a supported Python and a Fortran compiler:

```bash
python -m pip install --upgrade pip
python -m pip install .
```

The build uses the PEP 517 Meson backend.  A source installation requires a
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
contract.  Before modifying the Fortran algorithms or the scientific API, run:

```bash
python tests/reference/validate_legacy_baseline.py
```

The checked-in reference covers regular and Gaussian grids with both stored and
computed Legendre workspaces.  Details are in
[the scientific baseline document](docs/modernization/01-scientific-baseline.md).

## License and provenance

This repository is a mixed-license distribution.  It contains SPHEREPACK-
derived code under the UCAR/NCAR license and historical Python-binding code
under its original permission notice.  New maintained-project files use the
BSD 3-Clause license unless stated otherwise.  Read [LICENSE](LICENSE) and
[NOTICE](NOTICE) before redistributing the package.

## Modernization status

The modernization plan is tracked in [docs/modernization/README.md](docs/modernization/README.md).
Stage 2 makes the project an independent PEP 517/Meson distribution, removes
the obsolete `numpy.distutils` build, and preserves the legacy `spharm` import
path while the next stages modernize the Fortran source and public API.
