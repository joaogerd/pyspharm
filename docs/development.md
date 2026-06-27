# Development environment

## Requirements

Development requires CPython 3.10 or newer, a C compiler, `gfortran`, and
`ninja`. The package builds a NumPy F2PY extension through Meson.

## Editable installation

Install the build requirements in the same Python environment that will import
the package, then disable pip build isolation for the editable installation:

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade \
  "numpy>=1.26" \
  "meson-python>=0.15" \
  "meson>=1.1" \
  ninja \
  "pytest>=8" \
  "hypothesis[numpy]>=6.100"

python -m pip install --no-build-isolation -e ".[tests]"
python -m pytest
```

The `--no-build-isolation` flag is required for editable development builds.
Meson stores the NumPy C and F2PY include paths in the editable build directory
and may run `ninja` again at import time. Those paths must refer to the active,
persistent development environment rather than a temporary build-isolation
environment that pip removes after installation.

## Recovering from a failed editable build

Remove the editable package and its local build directory, then reinstall with
the supported command:

```bash
python -m pip uninstall -y pyspharm-ng
rm -rf build .mesonpy-*
python -m pip install --no-build-isolation -e ".[tests]"
python -m pytest
```

## Distribution build

A non-editable source or wheel build remains isolated and reproducible:

```bash
python -m pip install .
python -m pytest

python -m pip install build
python -m build
```

The distribution CI validates regular wheels, source distributions and the
legacy numerical reference contract. The editable workflow is validated
separately against the active development environment.
