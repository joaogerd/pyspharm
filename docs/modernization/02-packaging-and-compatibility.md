# Stage 2 — packaging and Python 3 compatibility

## Objective

Turn the historical source tree into an independently distributable PEP 517
package without changing the intended SPHEREPACK numerical calculations.

The distribution is named `pyspharm-ng`.  The public Python import remains
`import spharm` during this compatibility phase.  A separate modern `pyspharm`
API is deferred to Stage 4 so users can distinguish a packaging migration from
an API migration.

## Changes

- Meson and `meson-python` are the only supported build path.
- `setup.py` and `numpy.distutils` are removed.
- The compiled extension is installed as `spharm._spherepack`.
- NumPy and F2PY include paths are resolved directly from the build Python,
  without changing the current working directory.
- Expressions used as dimensions or Fortran workspace lengths use integer
  floor division under Python 3.
- Supported Python versions are 3.10–3.12.

## Installation contract

The CI must pass all of these paths:

1. install the source tree and run the test suite;
2. validate `legacy-contract-v1`;
3. build a wheel and an sdist with `python -m build`;
4. install the wheel in an empty virtual environment outside the checkout;
5. install the sdist in a separate empty virtual environment outside the
   checkout;
6. import `spharm`, locate `spharm._spherepack`, construct a transform and
   perform a scalar transform in both installed environments.

The resulting artifacts are uploaded by CI for review.  Passing source tests
alone is insufficient because it can accidentally import code from the working
tree instead of the installed wheel.

## Intentional compatibility boundaries

- `spharm` remains the supported import during Stages 2 and 3.
- `pyspharm-ng` is the package-manager distribution name and avoids taking over
  the unmaintained `pyspharm` project on PyPI.
- No silent float64 conversion, change of SPHEREPACK routine or change to
  physical conventions is included here.
- Changes to numerical output must continue to pass the Stage 1 baseline or
  start a new explicitly reviewed reference-contract version.
