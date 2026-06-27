# Changelog

All notable changes to the maintained `pyspharm-ng` distribution are recorded
here. Historical `pyspharm` releases predate this changelog.

## 0.1.0.dev0 — Unreleased

### Added

- Independent `pyspharm-ng` distribution metadata.
- Deterministic legacy numerical reference contract (`legacy-contract-v1`).
- CI coverage for source tests, wheel installation and source-distribution
  installation in isolated environments.
- Maintained `pyspharm` import path with `SphericalHarmonicTransform`.
- Explicit `as_real32` and `as_complex64` conversion helpers for the retained
  single-precision SPHEREPACK ABI.
- Scalar and wind transform methods with validated array ranks, shapes and
  triangular spectral-coefficient sizes.

### Changed

- The compiled F2PY module is installed as `spharm._spherepack`.
- Python 3 workspace-length calculations use integer floor division.
- Meson/PEP 517 is the only supported build path.
- The historical `spharm.Spharmt` API is now documented as a compatibility
  interface while remaining supported.

### Removed

- The obsolete `numpy.distutils`-based `setup.py` build path.
