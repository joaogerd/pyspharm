# Changelog

All notable changes to the maintained `pyspharm-ng` distribution are recorded
here. Historical `pyspharm` releases predate this changelog.

## 0.1.1.dev0 — Unreleased

### Added

- `SphericalHarmonicTransform.gradient` for zonal and meridional gradients
  synthesized from scalar spectral coefficients.
- `SphericalHarmonicTransform.streamfunction_velocity_potential` for
  streamfunction and velocity-potential diagnostics from horizontal wind.
- `pyspharm.regrid_scalar` for validated scalar spectral regridding between
  maintained transform configurations.
- `pyspharm.gaussian_latitudes_weights`, `pyspharm.spectral_indices`,
  `pyspharm.geodesic_points` and `pyspharm.interpolate_scalar` as maintained
  grid-metadata and point-interpolation utilities.
- Executable, command-line examples for regridding, geodesic points, a
  spherical-harmonic field and the Galewsky shallow-water case.
- Example smoke tests that run without an optional plotting dependency.
- Stage 7 documentation and equivalence tests against the legacy compatibility
  engine on regular and Gaussian grids.

### Fixed

- Synchronize the Meson project version with the PEP 621 package version.
- Derive `spharm.__version__` from installed distribution metadata.
- Document and continuously test the supported editable build workflow.
- Require matching Meson and package versions before stable release validation.

## 0.1.0 — 2026-06-27

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
- Portable manylinux x86_64 wheel builds and installed-wheel smoke tests for
  CPython 3.10, 3.11 and 3.12.
- A stable-tag GitHub Release workflow with tag/version/changelog validation.
- Release, support-scope and compatibility/deprecation policies.

### Changed

- The compiled F2PY module is installed as `spharm._spherepack`.
- Python 3 workspace-length calculations use integer floor division.
- Meson/PEP 517 is the only supported build path.
- The historical `spharm.Spharmt` API is now documented as a compatibility
  interface while remaining supported.

### Removed

- The obsolete `numpy.distutils`-based `setup.py` build path.
